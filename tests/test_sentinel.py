import json
import pytest
import datetime
from random import choice
from string import ascii_uppercase
from heart_rate_sentinel_server import get_app

def _new_patient_id():
    return ''.join(choice(ascii_uppercase) for _ in range(10))

@pytest.fixture()
def flask_app():
    app = get_app()
    return app


@pytest.fixture()
def patient_1_info():
    patient_1 = {
        "patient_id": 1,
        "attending_email": "random@duke.edu",
        "user_age": 21
    }
    return patient_1


@pytest.fixture()
def patient_2_info():
    patient_2 = {
        "patient_id": 2,
        "attending_email": "random@duke.edu",
        "user_age": 21
    }
    return patient_2


@pytest.fixture()
def heart_rate_p1():
    payload = {
        "patient_id": 1,
        "heart_rate": 80,
    }
    return payload


# tachychardic
@pytest.fixture()
def heart_rate_p2():
    payload = {
        "patient_id": 2,
        "heart_rate": 120,
    }
    return payload


def test_post_new_patient(flask_app, patient_1_info):
    client = flask_app.test_client()
    resp = client.post('/api/new_patient', json=patient_1_info)
    assert resp.status_code == 200


def test_post_new_patient_no_id(flask_app, patient_1_info):
    client = flask_app.test_client()
    patient = {
        "attending_email": "random@duke.edu",
        "user_age": 21
    }
    resp = client.post('/api/new_patient', json=patient)
    assert resp.json["status_code"] == 400


def test_post_new_patient_existing_id(flask_app, patient_1_info):
    p_id = _new_patient_id()
    new_patient = patient_1_info
    new_patient["patient_id"] = p_id
    client = flask_app.test_client()
    client.post('/api/new_patient', json=new_patient)
    resp = client.post('/api/new_patient', json=new_patient)

    assert resp.json["error_type"] == "ValueError"


def test_post_new_patient_no_email(flask_app):
    client = flask_app.test_client()
    patient = {
        "patient_id": 1230,
        "user_age": 21
    }
    resp = client.post('/api/new_patient', json=patient)
    assert resp.json["error_type"] == "AttributeError"


def test_post_new_patient_bad_email(flask_app, patient_1_info):
    p_id = _new_patient_id()
    new_patient = patient_1_info
    new_patient["patient_id"] = p_id
    new_patient["attending_email"] = "randomduke.edu"

    client = flask_app.test_client()
    resp = client.post('/api/new_patient', json=new_patient)
    assert resp.json["error_type"] == "ValueError"


def test_post_new_patient_no_age(flask_app):
    client = flask_app.test_client()
    patient = {
        "patient_id": 1230,
        "attending_email": "random@duke.edu",
    }
    resp = client.post('/api/new_patient', json=patient)
    assert resp.json["error_type"] == "AttributeError"


def test_post_heart_rate(flask_app, patient_1_info, heart_rate_p1):
    client = flask_app.test_client()
    client.post('/api/new_patient', json=patient_1_info)
    resp = client.post('/api/heart_rate', json=heart_rate_p1)
    assert resp.status_code == 200


def test_post_heart_rate_no_id(flask_app, patient_1_info, heart_rate_p1):
    client = flask_app.test_client()
    client.post('/api/new_patient', json=patient_1_info)
    payload = {
        "heart_rate": 100
    }
    resp = client.post('/api/heart_rate', json=payload)
    assert resp.json["error_type"] == "AttributeError"


def test_post_heart_rate_no_hr(flask_app, patient_1_info, heart_rate_p1):
    p_id = _new_patient_id()
    new_patient = patient_1_info
    new_patient["patient_id"] = p_id

    client = flask_app.test_client()
    client.post('/api/new_patient', json=new_patient)
    payload = {
        "patient_id": p_id
    }
    resp = client.post('/api/heart_rate', json=payload)
    assert resp.json["error_type"] == "AttributeError"


def test_get_interval_average(flask_app, patient_1_info, heart_rate_p1):
    client = flask_app.test_client()
    new_patient = patient_1_info
    p_id = ''.join(choice(ascii_uppercase) for _ in range(10))
    new_patient["patient_id"] = p_id
    client.post('/api/new_patient', json=new_patient)
    new_hr = heart_rate_p1
    new_hr["patient_id"] = p_id
    client.post('/api/heart_rate', json=new_hr)
    payload = {
        "patient_id": p_id,
        "heart_rate_average_since": datetime.datetime.now(),
    }
    resp = client.post('/api/heart_rate/interval_average', json=payload)
    assert resp.status_code == 200


def test_get_interval_average_no_id(flask_app, patient_1_info, heart_rate_p1):
    client = flask_app.test_client()
    new_patient = patient_1_info
    p_id = ''.join(choice(ascii_uppercase) for _ in range(10))
    new_patient["patient_id"] = p_id
    client.post('/api/new_patient', json=new_patient)
    new_hr = heart_rate_p1
    new_hr["patient_id"] = p_id
    client.post('/api/heart_rate', json=new_hr)
    payload = {
        "heart_rate_average_since": datetime.datetime.now(),
    }
    resp = client.post('/api/heart_rate/interval_average', json=payload)
    assert resp.json["error_type"] == "AttributeError"


def test_get_interval_average_no_time(flask_app, patient_1_info, heart_rate_p1):
    client = flask_app.test_client()
    new_patient = patient_1_info
    p_id = ''.join(choice(ascii_uppercase) for _ in range(10))
    new_patient["patient_id"] = p_id
    client.post('/api/new_patient', json=new_patient)
    new_hr = heart_rate_p1
    new_hr["patient_id"] = p_id
    client.post('/api/heart_rate', json=new_hr)
    payload = {
        "patient_id": p_id
    }
    resp = client.post('/api/heart_rate/interval_average', json=payload)
    assert resp.json["error_type"] == "AttributeError"


def test_get_status(flask_app, patient_1_info, heart_rate_p1):
    client = flask_app.test_client()
    new_patient = patient_1_info
    p_id = ''.join(choice(ascii_uppercase) for _ in range(10))
    new_patient["patient_id"] = p_id
    client.post('/api/new_patient', json=new_patient)
    new_hr = heart_rate_p1
    new_hr["patient_id"] = p_id
    client.post('/api/heart_rate', json=new_hr)
    resp = client.get('/api/status/{}'.format(patient_1_info["patient_id"]))

    assert resp.status_code == 200


def test_get_heart_rate(flask_app, patient_1_info, heart_rate_p1):
    client = flask_app.test_client()
    new_patient = patient_1_info
    p_id = ''.join(choice(ascii_uppercase) for _ in range(10))
    new_patient["patient_id"] = p_id
    client.post('/api/new_patient', json=new_patient)
    new_hr = heart_rate_p1
    new_hr["patient_id"] = p_id
    client.post('/api/heart_rate', json=new_hr)
    resp = client.get("/api/heart_rate/{}".format(p_id))
    assert resp.status_code == 200


def test_get_average(flask_app, patient_1_info, heart_rate_p1):
    client = flask_app.test_client()
    new_patient = patient_1_info
    p_id = ''.join(choice(ascii_uppercase) for _ in range(10))
    new_patient["patient_id"] = p_id
    client.post('/api/new_patient', json=new_patient)
    new_hr = heart_rate_p1
    new_hr["patient_id"] = p_id
    client.post('/api/heart_rate', json=new_hr)
    resp = client.get("/api/heart_rate/average/{}".format(p_id))
    assert resp.status_code == 200


@pytest.mark.parametrize("age, hr, expect", [
    (4, 190, True),
    (10, 130, True),
    (18, 110, True),
    (4, 80, False),
    (18, 80, False)
])
def test__is_tachychardic(age, hr, expect):
    from heart_rate_sentinel_server import _is_tachychardic
    assert _is_tachychardic(age, hr) == expect


@pytest.mark.parametrize("email, expect", [
    ("test@gmail.com", True),
    ("testgmail.com", False),
    ("test@gmailcom", False),
])
def test__is_valid_email(email, expect):
    from heart_rate_sentinel_server import _is_valid_email
    assert _is_valid_email(email) == expect


@pytest.mark.parametrize("age, expect", [
    (18, True),
    ("3", False),
    (2.5, False),
])
def test__is_valid_age(age, expect):
    from heart_rate_sentinel_server import _is_valid_age
    assert _is_valid_age(age) == expect


@pytest.mark.parametrize("heart_rate, expect", [
    (123, True),
    (123.4, False),
    (-345, False),
    ("test", False),
])
def test__is_valid_heart_rate(heart_rate, expect):
    from heart_rate_sentinel_server import _is_valid_heart_rate
    assert _is_valid_heart_rate(heart_rate) == expect
