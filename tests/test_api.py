import pytest
import hr_api
from random import choice
from string import ascii_uppercase


def _new_patient_id():
    return ''.join(choice(ascii_uppercase) for _ in range(10))


def test_get_all_patients():
    p_id = _new_patient_id()
    patient = hr_api.add_new_patient(p_id, "test@gmail.com", 21)
    assert hr_api.get_all_patients()[p_id]["patient_id"] == patient["patient_id"]


def test_add_new_patient():
    p_id = _new_patient_id()
    hr_api.add_new_patient(p_id, "test@gmail.com", 21)
    assert True


@pytest.mark.parametrize("inputs, error", [
    (("1", "testgmail.com", 21), ValueError),
    (("1234", "test@gmail.com", "21"), ValueError),
    (("3476", "test@gmail.com", 21.5), ValueError),
])
def test_add_new_patient_bad_inputs(inputs, error):
    with pytest.raises(error):
        hr_api.add_new_patient(inputs[0], inputs[1], inputs[2])


def test_get_interval_average():
    p_id = _new_patient_id()
    hr_api.add_new_patient(p_id, "test@gmail.com", 21)
    hr_api.post_heart_rate(p_id, 90)
    is_tach, time = hr_api.get_patient_status(p_id)
    hr_api.post_heart_rate(p_id, 100)
    avg = hr_api.get_interval_average(p_id, time)
    assert avg == 90


def test_get_interval_average_no_exist():
    p_id = _new_patient_id()
    with pytest.raises(ValueError):
        hr_api.get_interval_average(p_id, 90)


def test_post_heart_rate():
    p_id = _new_patient_id()
    hr_api.add_new_patient(p_id, "test@gmail.com", 21)
    resp = hr_api.post_heart_rate(p_id, 90)
    assert resp["heart_rates"] == [90]


@pytest.mark.parametrize("heart_rate, error", [
    (21.5, TypeError),
    ("21", TypeError),
    (-1, ValueError),
])
def test_post_heart_rate_bad(heart_rate, error):
    p_id = _new_patient_id()
    hr_api.add_new_patient(p_id, "test@gmail.com", 21)
    with pytest.raises(error):
        hr_api.post_heart_rate(p_id, heart_rate)


def test_get_patient_status():
    p_id = _new_patient_id()
    hr_api.add_new_patient(p_id, "test@gmail.com", 21)
    hr_api.post_heart_rate(p_id, 90)

    is_tach, time = hr_api.get_patient_status(p_id)
    assert is_tach == False


def test_get_patient_status_no_hr():
    p_id = _new_patient_id()
    hr_api.add_new_patient(p_id, "test@gmail.com", 21)
    is_tach, time = hr_api.get_patient_status(p_id)
    assert is_tach is None and time is None


def test_get_heart_rate():
    p_id = _new_patient_id()
    hr_api.add_new_patient(p_id, "test@gmail.com", 21)
    hr_api.post_heart_rate(p_id, 90)

    resp = hr_api.get_heart_rate(p_id)
    assert resp == [90]


def test_get_heart_rate_no_exist():
    p_id = _new_patient_id()
    with pytest.raises(ValueError):
        hr_api.post_heart_rate(p_id, 90)


def test_get_heart_rate_average():
    p_id = _new_patient_id()
    hr_api.add_new_patient(p_id, "test@gmail.com", 21)
    hr_api.post_heart_rate(p_id, 80)
    hr_api.post_heart_rate(p_id, 90)
    hr_api.post_heart_rate(p_id, 100)
    hr_api.post_heart_rate(p_id, 110)

    resp = hr_api.get_heart_rate_average(p_id)
    assert resp == 95


def test_get_heart_rate_average_no_exist():
    p_id = _new_patient_id()
    with pytest.raises(ValueError):
        hr_api.get_heart_rate_average(p_id)


@pytest.mark.parametrize("json_info, error", [
    ({"error_type": "TypeError", "msg": "Test"}, TypeError),
    ({"error_type": "ValueError", "msg": "Test"}, ValueError),
    ({"error_type": "AttributeError", "msg": "Test"}, AttributeError),
])
def test_error_catcher(json_info, error):
    with pytest.raises(error):
        hr_api.error_catcher(json_info)
