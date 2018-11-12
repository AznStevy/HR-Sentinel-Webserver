import pytest
import hrs_db
from random import choice
from string import ascii_uppercase
from hrs_db import HRMDatabase

pytestmark = pytest.mark.asyncio


# define new database to not screw up production db
@pytest.fixture()
async def TestHRMDatabase():
    # first clear and then reinitialize
    database = HRMDatabase("test_hrm_database")
    await database.drop()
    database = HRMDatabase("test_hrm_database")
    return database


async def test_add_patient(TestHRMDatabase):
    patient_id = ''.join(choice(ascii_uppercase) for _ in range(10))
    test_patient = {
        "patient_id": patient_id,
        "user_age": 24,
        "attending_email": "myemail@fun.com"
    }
    assert test_patient == await TestHRMDatabase.add_patient(test_patient)


async def test_add_patient_repeat_id(TestHRMDatabase):
    test_patient = {
        "patient_id": "3234NMK",
        "user_age": 24,
        "attending_email": "myemail@fun.com"
    }
    with pytest.raises(AttributeError):
        await TestHRMDatabase.add_patient(test_patient)
        await TestHRMDatabase.add_patient(test_patient)


@pytest.mark.parametrize("user_age, error_type", [
    ("test", TypeError), (10.2, TypeError),
    ([1, 2, 3], TypeError), (0, ValueError),
    (-2, ValueError), (400, ValueError),
])
async def test_add_patient_bad_age(TestHRMDatabase, user_age, error_type):
    patient_id = ''.join(choice(ascii_uppercase) for _ in range(10))
    test_patient = {
        "patient_id": patient_id,
        "user_age": user_age,
        "attending_email": "myemail@fun.com"
    }
    with pytest.raises(error_type):
        await TestHRMDatabase.add_patient(test_patient)


@pytest.mark.parametrize("attending_email, error_type", [
    (-2, ValueError), ("testcom", ValueError),
])
async def test_add_patient_bad_email(TestHRMDatabase, attending_email, error_type):
    patient_id = ''.join(choice(ascii_uppercase) for _ in range(10))
    test_patient = {
        "patient_id": patient_id,
        "user_age": 24,
        "attending_email": attending_email
    }
    with pytest.raises(error_type):
        await TestHRMDatabase.add_patient(test_patient)


async def test_remove_patient_exists():
    # add the patient
    patient_id = ''.join(choice(ascii_uppercase) for _ in range(10))
    test_patient = {
        "patient_id": patient_id,
        "user_age": 24,
        "attending_email": "myemail@fun.com"
    }
    await TestHRMDatabase.add_patient(test_patient)
    assert await TestHRMDatabase.remove_patient(patient_id)


async def test_remove_patient_not_exists():
    patient_id = "-thisidcan'tberandomlygenerated"
    assert not await TestHRMDatabase.remove_patient(patient_id)


async def test_get_patient():
    # add the patient
    patient_id = ''.join(choice(ascii_uppercase) for _ in range(10))
    test_patient = {
        "patient_id": patient_id,
        "user_age": 24,
        "attending_email": "myemail@fun.com"
    }
    await TestHRMDatabase.add_patient(test_patient)

    retrieved_patient = TestHRMDatabase.get_patient(patient_id)
    assert retrieved_patient["patient_id"] == test_patient["patient_id"]
