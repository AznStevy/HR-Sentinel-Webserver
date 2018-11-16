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
    resp = get("all_patients")
    return byte_2_json(resp)


def add_new_patient(patient_id: str, attending_email: str, user_age: int):
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
    return byte_2_json(resp)


def get_interval_average(patient_id: str, timestamp: str):
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
    return byte_2_json(resp)


def post_heart_rate(patient_id: str, heart_rate: int):
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
    return byte_2_json(resp)


def get_patient_status(patient_id: str):
    """
    Obtains patient status. Sends email if tachychardic.
    Args:
        patient_id: ID of the patient.

    Returns:
        tuple: first is if tachychardic, second is timestamp.

    """
    resp = get("status/{}".format(patient_id))
    return byte_2_json(resp)


def get_heart_rate(patient_id: str):
    """
    Obtains all heart rates from the
    Args:
        patient_id: ID of the patient.

    Returns:
        list: List of all heart rates from the patient.

    """
    resp = get("heart_rate/{}".format(patient_id))
    return byte_2_json(resp)


def get_heart_rate_average(patient_id: str):
    """
    Obtains an average heart rate of the patient.
    Args:
        patient_id: ID of the patient.

    Returns:
        float: Average heart rate of the patient.
    """
    resp = get("heart_rate/average/{}".format(patient_id))
    return byte_2_json(resp)


def byte_2_json(resp):
    """
    Converts bytes to json. Raises exception if necessary.
    Args:
        resp (bytes): Response from request.

    Returns:
        dict: Json object of interest.

    """
    json_resp = json.loads(resp.content.decode('utf-8'))
    json_resp = error_catcher(json_resp)
    return json_resp


def error_catcher(json_resp: dict):
    """
    Raises appropriate exceptions from the web server.
    Args:
        json_resp: Information from the server.

    Returns:
        dict: The original dictionary if not error.

    """
    if type(json_resp) == dict and "error_type" in json_resp.keys():
        if "TypeError" in json_resp["error_type"]:
            raise TypeError(json_resp["msg"])
        if "AttributeError" in json_resp["error_type"]:
            raise AttributeError(json_resp["msg"])
        if "ValueError" in json_resp["error_type"]:
            raise ValueError(json_resp["msg"])
    return json_resp


if __name__ == "__main__":
    from random import choice
    from string import ascii_uppercase

    p_id = ''.join(choice(ascii_uppercase) for _ in range(10))
    print(p_id)
    r = add_new_patient(p_id, "szx2@duke.edu", 21)
    print(r)
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
