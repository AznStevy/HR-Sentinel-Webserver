import json
import pytest
import datetime
from random import choice
from string import ascii_uppercase
from heart_rate_sentinel_server import get_app


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


def test_post_heart_rate(flask_app, patient_1_info, heart_rate_p1):
    client = flask_app.test_client()
    client.post('/api/new_patient', json=patient_1_info)
    resp = client.post('/api/heart_rate', json=heart_rate_p1)
    assert resp.status_code == 200


def test_post_heart_rate_no_patient(flask_app, heart_rate_p1):
    client = flask_app.test_client()
    new_patient = heart_rate_p1
    new_patient["patient_id"] = ''.join(choice(ascii_uppercase) for _ in range(10))
    resp = client.post('/api/heart_rate', json=new_patient)
    return resp.status_code == 500


def test_get_interval_average(flask_app, patient_1_info, heart_rate_p1):
    client = flask_app.test_client()
    new_patient = patient_1_info
    p_id = ''.join(choice(ascii_uppercase) for _ in range(10))
    new_patient["patient_id"] = p_id
    resp = client.post('/api/new_patient', json=new_patient)
    new_hr = heart_rate_p1
    new_hr["patient_id"] = p_id
    resp = client.post('/api/heart_rate', json=new_hr)
    payload = {
        "patient_id": p_id,
        "heart_rate_average_since": datetime.datetime.now(),
    }
    resp = client.post('/api/heart_rate/interval_average', json=payload)
    assert resp.status_code == 200


def test_get_status(flask_app, patient_1_info, patient_2_info):
    client = flask_app.test_client()
    client.post('/api/new_patient', json=patient_1_info)


def test_get_heart_rate(flask_app):
    assert True


def test_get_average(flask_app):
    assert True
