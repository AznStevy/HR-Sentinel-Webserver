import json
import datetime
import sendgrid
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
patients = {}


# for testing
@app.route("/api/all_patients", methods=["GET"])
def get_all():
    """
    Gets all patients from the database.
    Returns:
        dict: All patients in the database. Key by ID.

    """
    return jsonify(patients)


@app.route("/api/status/<patient_id>", methods=["GET"])
def get_status(patient_id):
    """
    Returns the status of the patient's most recent heart rate
    Args:
        patient_id (str): Status of the patient ID to retrieve.

    Returns:
        tuple: First element is if tachycardic, second element is timestamp.
    """

    # patient = await self.database.get_patient(patient_id)
    if patient_id not in patients.keys():
        return None
    patient = patients[patient_id]

    patient_age = patient["user_age"]
    recent_hr = patient["heart_rates"][-1]
    recent_hr_timestamp = patient["timestamps"][-1]

    is_tachycardic = _is_tachychardic(patient_age, recent_hr)
    if is_tachycardic:
        to_email = patient["attending_email"]
        email_content = "Patient with ID {} is tachychardic.".format(patient_id)
        send_email(to_email,
                   email_subject="Patient Tachychardic",
                   email_content=email_content)
    return jsonify((is_tachycardic, recent_hr_timestamp))


def _is_tachychardic(age: int, heart_rate: int):
    """
    Determines if user is tachychardic based on age and heart rate. Based on:
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
    if patient_id not in patients.keys():
        return None
    patient = patients[patient_id]

    all_heartrates = patient["heart_rates"]
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
    # patient = await self.database.get_patient(patient_id)
    if patient_id not in patients.keys():
        return None
    patient = patients[patient_id]

    all_heartrates = patient["heart_rates"]
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
        raise AttributeError("Must contain patient_id.")
    if "heart_rate_average_since" not in content.keys():
        raise AttributeError("Must contain heart_rate_average_since")

    patient_id = str(content["patient_id"])
    heart_rate_ts = str(content["heart_rate_average_since"])

    # get patient
    # patient = await self.database.get_patient(patient_id)
    if patient_id not in patients.keys():
        return None
    patient = patients[patient_id]

    before_hrs = []
    # print("Current timestamps: ", patient["timestamps"], "Compare to: ", heart_rate_ts)
    for i, timestamp in enumerate(patient["timestamps"]):
        if heart_rate_ts >= timestamp:
            print(heart_rate_ts, timestamp)
            before_hrs.append(patient["heart_rates"][i])

    if len(before_hrs) < 0:
        return None

    return jsonify(sum(before_hrs) / len(before_hrs))


@app.route("/api/new_patient", methods=["POST"])
def post_new_patient():
    """
    Adds new patient to the database.
    """
    new_patient = request.get_json()

    if "patient_id" not in new_patient:
        raise AttributeError("Must have patient_id.")
    if "attending_email" not in new_patient:
        raise AttributeError("Must have attending_email.")
    elif "@" not in new_patient["attending_email"]:
        raise ValueError("Invalid email.")
    if "user_age" not in new_patient:
        raise AttributeError("Must have user_age.")

    patient_id = new_patient["patient_id"]
    new_patient["timestamps"] = []
    new_patient["heart_rates"] = []
    patients[patient_id] = new_patient
    return jsonify(new_patient)

    # mongo stuff
    """
    try:
        pass
        # await self.database.add_patient(new_patient)
    except TypeError as e:
        pass
    except AttributeError as e:
        pass
    except ValueError as e:
        pass"""


@app.route("/api/heart_rate", methods=["POST"])
def post_heart_rate():
    """
    Posts new heart rate for a patient.
    """
    updated_heartrate = request.get_json()

    if "patient_id" not in updated_heartrate:
        raise AttributeError("Must have patient_id.")

    patient_id = updated_heartrate["patient_id"]
    if patient_id not in patients.keys():
        raise ValueError("Patient does not exist yet.")

    if "heart_rate" not in updated_heartrate:
        raise AttributeError("Must have heart_rate.")
    new_hr = updated_heartrate["heart_rate"]
    if type(new_hr) != int:
        raise TypeError("heart_rate must be type int.")
    if new_hr < 0:
        raise ValueError("Invalid heart rate.")

    new_hr = updated_heartrate["heart_rate"]
    new_timestamp = str(datetime.datetime.now())
    patients[patient_id]["heart_rates"].append(new_hr)
    patients[patient_id]["timestamps"].append(new_timestamp)
    return jsonify(patients[patient_id])

    # ---------- mongo stuff -------------
    """
    try:
        pass
        # await self.database.update_patient(content)
    except TypeError as e:
        pass
    except AttributeError as e:
        pass
    except ValueError as e:
        pass"""


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


def get_app():
    """
    Gets the app (for testing).
    Returns:
        object: Flask application object.
    """
    return app


if __name__ == "__main__":
    app.run(host="127.0.0.1")
