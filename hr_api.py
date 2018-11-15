import json
import requests

post_url = "http://127.0.0.1:5000/api/"


# ---------- general web interfacing ----------------------

def post(endpoint, payload, uri="http://127.0.0.1:5000/api/"):
    """
    Posts to the flask web server.
    Args:
        endpoint: The endpoint of the API
        payload: Payload according to what the web server requires.
        uri: Web server uri.

    Returns:
        object: Response from web server.

    """
    return requests.post(uri + endpoint, json=payload)


def get(endpoint, uri="http://127.0.0.1:5000/api/"):
    """
    Gets from the flask web server.
    Args:
        endpoint: The endpoint of the API
        uri: Web server uri.

    Returns:
        object: Response from web server.
    """
    return requests.get(uri + endpoint)


# ---------- API ----------------------
def get_all_patients():
    """
    Obtains a list of all patients in the database. (For testing)
    Returns:
        dict: All patients currently in database referenced by ID.

    """
    all_patients = get("all_patients").content.decode('utf-8')
    return json.loads(all_patients)


def add_new_patient(patient_id, attending_email, user_age):
    """
    Adds new patient to the database.
    Args:
        patient_id: ID of the patient.
        attending_email: Email of the user
        user_age: Age of the user.

    Returns:
        dict: Patient that added.
    """
    payload = {
        "patient_id": patient_id,
        "attending_email": attending_email,
        "user_age": user_age
    }
    resp = post("new_patient", payload)
    return json.loads(resp.content.decode('utf-8'))


def get_interval_average(patient_id, timestamp):
    """
    Gets the average heart rate from before a timestamp.
    Args:
        patient_id: ID of the patient.
        timestamp: timestamp in form YYYY-MM-DD HH:MM:SS.#######

    Returns:
        float: Average heart rate from before the timestamp.
    """
    payload = {
        "patient_id": patient_id,
        "heart_rate_average_since": timestamp,
    }
    resp = post("heart_rate/interval_average", payload)
    return json.loads(resp.content.decode('utf-8'))


def post_heart_rate(patient_id, heart_rate):
    """
    Posts a heart rate to a patient. Timestamp automatically generated.
    Args:
        patient_id: ID of the patient.
        heart_rate: Heart rate to post.

    Returns:
        dict: Updated patient information.

    """
    payload = {
        "patient_id": patient_id,
        "heart_rate": heart_rate,
    }
    resp = post("heart_rate", payload)
    return json.loads(resp.content.decode('utf-8'))


def get_patient_status(patient_id):
    """
    Obtains patient status. Sends email if tachychardic.
    Args:
        patient_id: ID of the patient.

    Returns:
        tuple: first is if tachychardic, second is timestamp.

    """
    resp = get("status/{}".format(patient_id))
    return json.loads(resp.content.decode('utf-8'))


def get_heart_rate(patient_id):
    """
    Obtains all heart rates from the
    Args:
        patient_id: ID of the patient.

    Returns:
        list: List of all heart rates from the patient.

    """
    resp = get("heart_rate/{}".format(patient_id))
    return json.loads(resp.content.decode('utf-8'))


def get_heart_rate_average(patient_id):
    """
    Obtains an average heart rate of the patient.
    Args:
        patient_id: ID of the patient.

    Returns:
        float: Average heart rate of the patient.
    """
    resp = get("heart_rate/average/{}".format(patient_id))
    return json.loads(resp.content.decode('utf-8'))


if __name__ == "__main__":
    from random import choice
    from string import ascii_uppercase

    p_id = ''.join(choice(ascii_uppercase) for _ in range(10))
    print(p_id)
    # p_id = "UZNUWUPQPI"
    r = add_new_patient(p_id, "szx2@duke.edu", 21)
    print(get_all_patients())
    r = post_heart_rate(p_id, 80)
    print("Posted: ", r)
    hr = get_heart_rate(p_id)
    print("All Heartrates:", hr)
    r = post_heart_rate(p_id, 90)
    print("Posted: ", r)
    av = get_heart_rate_average(p_id)
    print("Average: ", av)
    hr = get_heart_rate(p_id)
    print("All Heartrates:", hr)

    curr_status, timestamp = get_patient_status(p_id)
    print("Current Status 1 (False/Not Tach): ", curr_status, "Timestamp: ", timestamp)
    int_avg = get_interval_average(p_id, timestamp)
    print("Interval Average (should be 85):", int_avg)

    r = post_heart_rate(p_id, 100)
    print("Posted: ", r)
    hr = get_heart_rate(p_id)
    print("All Heartrates:", hr)
    r = post_heart_rate(p_id, 110)

    curr_status, _ = get_patient_status(p_id)
    print("Current Status 2 (True/Tach + sends email): ", curr_status, "Timestamp: ", timestamp)
    av = get_heart_rate_average(p_id)
    print("Average (95): ", av)
    int_avg = get_interval_average(p_id, timestamp)
    print("Interval Average (should be 85):", int_avg)
