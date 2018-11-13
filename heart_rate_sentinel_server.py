import os
import json
import hrs_db
import asyncio
import datetime
import sendgrid
from sendgrid.helpers.mail import *
from flask import Flask, request, jsonify


class HRMSentinelAPI(object):
    def __init__(self, **kwargs):
        app_name = kwargs.get("name", "heart_rate_sentinel_server")
        # self.database = hrs_db(app_name)
        self.app = Flask(app_name)  # some unique identifier
        with open("config.json", 'r') as f:
            config_info = json.load(f)
        self.sendgrid_API_KEY = config_info["SENDGRID_API_KEY"]
        self.from_email = config_info["from_email"]

        # testing in memory
        self.patients = {}

    def run(self):
        self.app.run(host="127.0.0.1")

    def _add_url_rules(self):
        self.app.add_url_rule('/api/', 'status/<patient_id>', self.get_status, options=["GET"])
        self.app.add_url_rule('/api/', 'heart_rate/<patient_id>', self.get_heart_rate, options=["GET"])
        self.app.add_url_rule('/api/', 'heart_rate/average/<patient_id>', self.get_average, options=["GET"])
        self.app.add_url_rule('/api/', 'heart_rate/interval_average', self.post_interval_average, options=["POST"])
        self.app.add_url_rule('/api/', 'new_patient', self.post_new_patient, options=["POST"])
        self.app.add_url_rule('/api/', 'heart_rate', self.post_heart_rate, options=["POST"])

    async def get_status(self, patient_id):
        """
        Returns the status of the patient's most recent heart rate
        Args:
            patient_id (str): Status of the patient ID to retrieve.

        Returns:
            tuple: First element is if tachycardic, second element is timestamp.
        """
        # patient = await self.database.get_patient(patient_id)
        if patient_id not in self.patients:
            return None
        patient = self.patients[patient_id]

        patient_age = patient["user_age"]
        recent_hr = patient["heart_rates"][-1]
        recent_hr_timestamp = patient["timestamps"][-1]

        is_tachycardic = self._is_tachychardic(patient_age, recent_hr)
        if is_tachycardic:
            to_email = patient["attending_email"]
            email_content = "Patient with ID {} is tachychardic.".format(patient_id)
            await self.send_email(to_email,
                                  email_subject="Patient Tachychardic",
                                  email_content=email_content)
        return (is_tachycardic, recent_hr_timestamp)

    def _is_tachychardic(self, age: int, heart_rate: int):
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

    async def get_heart_rate(self, patient_id: str):
        """
        Gets all heart rates that were recorded for a patient.
        Args:
            patient_id (str): Patient to retrieve info for.

        Returns:
            list: List of all heartrates for the patient.

        """
        # patient = await self.database.get_patient(patient_id)
        if patient_id not in self.patients:
            return None
        patient = self.patients[patient_id]

        all_heartrates = patient["heart_rates"]
        return all_heartrates

    async def get_average(self, patient_id):
        """
        Gets the average heart rate of all recorded heart rates for a patient
        Args:
            patient_id (str): Patient to retrieve info for.

        Returns:
            float: Average heart rate.
        """
        # patient = await self.database.get_patient(patient_id)
        if patient_id not in self.patients:
            return None
        patient = self.patients[patient_id]

        all_heartrates = patient["heart_rates"]
        return sum(all_heartrates) / len(all_heartrates)

    # ---------- post stuff ----------

    async def post_interval_average(self):
        """
        Retrieves the average heart rate for all recordings before timestamp.
        Returns:
            float: Average heart rate in interval.

        """
        content = request.json
        if "patient_id" not in content.keys():
            raise AttributeError("Must contain patient_id.")
        if "heart_rate_average_since" not in content.keys():
            raise AttributeError("Must contain heart_rate_average_since")

        patient_id = str(content["patient_id"])
        heart_rate_ts = str(content["heart_rate_average_since"])

        # get patient
        # patient = await self.database.get_patient(patient_id)
        if patient_id not in self.patients:
            return None
        patient = self.patients[patient_id]

        before_hrs = []
        for i, timestamp in enumerate(patient["timestamps"]):
            if heart_rate_ts <= timestamp:
                before_hrs.append(patient["heart_rates"][i])

        # find all before
        return sum(before_hrs) / len(before_hrs)

    async def post_new_patient(self):
        """
        Adds new patient to the database.
        """
        new_patient = request.json

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
        self.patients[patient_id] = new_patient

        # mongo stuff
        try:
            pass
            # await self.database.add_patient(new_patient)
        except TypeError as e:
            pass
        except AttributeError as e:
            pass
        except ValueError as e:
            pass

    async def post_heart_rate(self):
        """
        Posts new heart rate for a patient.
        """
        updated_heartrate = request.json

        if "patient_id" not in updated_heartrate:
            raise AttributeError("Must have patient_id.")
        if "patient_id" not in self.patients:
            raise ValueError("Patient does not exist yet.")
        if "heart_rate" not in updated_heartrate:
            raise AttributeError("Must have heart_rate.")
        elif type("heart_rate") != int:
            raise TypeError("heart_rate must be type int.")
        elif updated_heartrate["heart_rate"] < 0:
            raise ValueError("Invalid heart rate.")

        patient_id = updated_heartrate["patient_id"]
        new_hr = updated_heartrate["heart_rate"]
        new_timestamp = str(datetime.now())
        self.patients[patient_id]["heart_rates"].append(new_hr)
        self.patients[patient_id]["timestamps"].append(new_timestamp)
        # ---------- mongo stuff -------------
        try:
            pass
            # await self.database.update_patient(content)
        except TypeError as e:
            pass
        except AttributeError as e:
            pass
        except ValueError as e:
            pass

    async def send_email(self, to_address: str, email_subject: str, email_content: str):
        sg = sendgrid.SendGridAPIClient(apikey=self.sendgrid_API_KEY)
        from_email = Email(self.from_email)
        to_email = Email(to_address)
        content = Content("text/plain", email_content)
        mail = Mail(self.from_email, email_subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())


if __name__ == "__main__":
    sentinel_api = HRMSentinelAPI()
    sentinel_api.run()
