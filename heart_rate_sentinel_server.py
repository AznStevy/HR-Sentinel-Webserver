import json
import datetime
import sendgrid
from hrs_db import HRDatabase
from sendgrid.helpers.mail import *
from flask import Flask, request, jsonify

app_name = "heart_rate_sentinel_server"
# self.database = hrs_db(app_name)
app = Flask(app_name)

# read in credentials, screws with tests.
try:
    with open("config.json", 'r') as f:
        config_info = json.load(f)
    sendgrid_API_KEY = config_info["SENDGRID_API_KEY"]
    from_email = config_info["from_email"]
except:
    pass

# testing in memory
# patients = {}

# testing using DM
patients = HRDatabase()


# for testing
@app.route("/api/all_patients", methods=["GET"])
def get_all():
    """
    Gets all patients from the database.
    Returns:
        dict: All patients in the database. Key by ID.

    """
    return jsonify(patients.get_all())


@app.route("/api/status/<patient_id>", methods=["GET"])
def get_status(patient_id):
    """
    Returns the status of the patient's most recent heart rate
    Args:
        patient_id (str): Status of the patient ID to retrieve.

    Returns:
        tuple: First element is if tachycardic, second element is timestamp.
    """

    patient = patients.get_patient(patient_id)
    if patient is None:
        return error_handler(500, "User does not exist.", "ValueError")
    patient_age = patient.user_age

    if patient.heart_rates == []:
        return jsonify((None, None))
    recent_hr = patient.heart_rates[-1]
    recent_hr_timestamp = patient.timestamps[-1]

    is_tachycardic = _is_tachychardic(patient_age, recent_hr)
    if is_tachycardic:
        to_email = patient.attending_email
        email_content = "Patient with ID {} is tachychardic.".format(patient_id)
        send_email(to_email,
                   email_subject="Patient Tachychardic",
                   email_content=email_content)
    return jsonify((is_tachycardic, recent_hr_timestamp))


def _is_tachychardic(age: int, heart_rate: int):
    """
    Determines if user is tacahychardic based on age and heart rate. Based on:
    https://pediatricheartspecialists.com/heart-education/18-arrhythmia/177-sinus-tachycardia
    Args:
        age (int): Age of the user.
        heart_rate (int): Heartrate of the user.

    Returns:
        bool: Whether or not the user is tachychardic .

    """
    if age <= 6 and heart_rate >= 160:
        return True
    elif 6 < age <= 17 and heart_rate >= 120:
        return True
    elif age > 17 and heart_rate >= 100:
        return True
    return False


@app.route("/api/heart_rate/<patient_id>", methods=["GET"])
def get_heart_rate(patient_id: str):
    """
    Gets all heart rates that were recorded for a patient.
    Args:
        patient_id (str): Patient to retrieve info for.

    Returns:
        list: List of all heartrates for the patient.

    """
    # patient = await self.database.get_patient(patient_id)
    patient = patients.get_patient(patient_id)
    if patient is None:
        return error_handler(500, "User does not exist.", "ValueError")

    all_heartrates = patient.heart_rates
    return jsonify(all_heartrates)


@app.route("/api/heart_rate/average/<patient_id>", methods=["GET"])
def get_average(patient_id):
    """
    Gets the average heart rate of all recorded heart rates for a patient
    Args:
        patient_id (str): Patient to retrieve info for.

    Returns:
        float: Average heart rate.
    """
    patient = patients.get_patient(patient_id)
    if patient is None:
        return error_handler(500, "User does not exist.", "ValueError")

    all_heartrates = patient.heart_rates
    if not all_heartrates:
        return jsonify({})
    return jsonify(sum(all_heartrates) / len(all_heartrates))


# ---------- post stuff ----------
@app.route("/api/heart_rate/interval_average", methods=["POST"])
def post_interval_average():
    """
    Retrieves the average heart rate for all recordings before timestamp.
    Returns:
        dict: Original content with average heart rate in interval.

    """
    content = request.get_json()
    if "patient_id" not in content.keys():
        return error_handler(400, "Must contain patient_id.", "AttributeError")
    if "heart_rate_average_since" not in content.keys():
        return error_handler(400, "Must contain heart_rate_average_since", "AttributeError")

    patient_id = str(content["patient_id"])
    heart_rate_ts = str(content["heart_rate_average_since"])

    # get patient
    # patient = await self.database.get_patient(patient_id)
    patient = patients.get_patient(patient_id)
    if patient is None:
        return error_handler(500, "User does not exist.", "ValueError")

    before_hrs = []
    # print("Current timestamps: ", patient["timestamps"], "Compare to: ", heart_rate_ts)
    for i, timestamp in enumerate(patient.timestamps):
        if heart_rate_ts >= timestamp:
            before_hrs.append(patient.heart_rates[i])

    if len(before_hrs) < 0:
        return jsonify(None)

    return jsonify(sum(before_hrs) / len(before_hrs))


@app.route("/api/new_patient", methods=["POST"])
def post_new_patient():
    """
    Adds new patient to the database.
    """
    new_patient = request.get_json()

    if "patient_id" not in new_patient:
        return error_handler(400, "Must contain patient_id.", "AttributeError")

    patient_id = new_patient["patient_id"]
    patient = patients.get_patient(patient_id)

    if patient is not None:
        return error_handler(400, "Patient Already Exists!", "ValueError")
    if "attending_email" not in new_patient:
        return error_handler(400, "Must have attending_email.", "AttributeError")
    elif not _is_valid_email(new_patient["attending_email"]):
        return error_handler(400, "Invalid email.", "ValueError")
    if "user_age" not in new_patient:
        return error_handler(400, "Must have user_age.", "AttributeError")
    elif not _is_valid_age(new_patient["user_age"]):
        return error_handler(400, "Invalid user_age.", "ValueError")

    patients.add_patient(new_patient)
    return jsonify(new_patient)


@app.route("/api/heart_rate", methods=["POST"])
def post_heart_rate():
    """
    Posts new heart rate for a patient.
    """
    updated_heartrate = request.get_json()

    if "patient_id" not in updated_heartrate:
        return error_handler(400, "Must have patient_id.", "AttributeError")

    patient_id = updated_heartrate["patient_id"]
    patient = patients.get_patient(patient_id)
    if patient is None:
        return error_handler(400, "Patient does not exist yet.", "ValueError")

    if "heart_rate" not in updated_heartrate:
        return error_handler(400, "Must have heart_rate.", "AttributeError")

    new_hr = updated_heartrate["heart_rate"]
    if type(new_hr) != int:
        return error_handler(400, "heart_rate must be type int.", "TypeError")
    if new_hr < 0:
        return error_handler(400, "Invalid heart rate.", "ValueError")

    new_hr = updated_heartrate["heart_rate"]
    new_timestamp = str(datetime.datetime.now())

    patients.add_hr(patient_id, new_hr, new_timestamp)
    patient = patients.get_patient(patient_id)
    updated_info = patients.convert_to_json(patient)
    return jsonify(updated_info)


def send_email(to_address: str, email_subject: str, email_content: str):
    """
    Sends email regarding heart rate via Sendgrid API.
    Args:
        to_address: Address to send to
        email_subject: Subject of the email.
        email_content: Content of the email.

    Returns:
        object: API response from Sendgrid Server.
    """
    sg = sendgrid.SendGridAPIClient(apikey=sendgrid_API_KEY)
    from_email = config_info["from_email"]
    from_email = Email(from_email)

    to_email = Email(to_address)

    content = Content("text/plain", email_content)

    mail = Mail(from_email, email_subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response


def _is_valid_email(email):
    """
    Determines if the email is valid.
    Args:
        email: Email to test.

    Returns:
        bool: If the email is valid.

    """
    if "@" not in email:
        return False
    if "." not in email:
        return False
    return True


def _is_valid_age(user_age):
    """
    Determines if the age is valid.
    Args:
        user_age: Age to test.

    Returns:
        bool: If the age is valid.

    """
    if type(user_age) != int:
        return False
    elif user_age < 0:
        return False
    return True


def _is_valid_heart_rate(heart_rate):
    """
    Determines if the heart rate is valid.
    Args:
        heart_rate: Heart rate in question.

    Returns:
        bool: Whether or not the heart rate is valid.

    """
    if type(heart_rate) != int:
        return False
    if heart_rate < 0:
        return False
    return True


def _is_valid_timestamp(timestamp):
    """
    Determines if the timestamp for is valid.
    Args:
        timestamp (str): Time stamp string in question

    Returns:
        bool: Whether or not the time stamp is valid.

    """
    if type(timestamp) != str:
        return False
    return True


def error_handler(status_code, msg, error_type):
    """
    Handles errors to send back to requester.
    Args:
        status_code: The status code, standard.
        msg: Message to send.
        error_type: Error type if raises exception.

    Returns:
        dict: Error message information.

    """
    error_msg = {
        "status_code": status_code,
        "msg": msg,
        "error_type": error_type
    }
    return jsonify(error_msg)


def get_app():
    """
    Gets the app (for testing).
    Returns:
        object: Flask application object.
    """
    return app


if __name__ == "__main__":
    app.run(host="127.0.0.1")
