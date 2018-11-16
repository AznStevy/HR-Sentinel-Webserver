import json
from pymodm import connect
from pymodm import MongoModel, fields


class Patient(MongoModel):
    patient_id = fields.CharField(primary_key=True)
    attending_email = fields.EmailField()
    user_age = fields.IntegerField()
    heart_rates = fields.ListField()
    timestamps = fields.ListField()


class HRDatabase(object):
    def __init__(self):
        with open("config.json", 'r') as f:
            config_info = json.load(f)
            db_user = config_info["mongo_user"]
            db_pass = config_info["mongo_pass"]

            url = "mongodb://{}:{}@ds041337.mlab.com:41337/heart_rate_sentinel".format(
                db_user, db_pass)
            connect(url)

    def get_all(self):
        """
        Obtains a dictionary of every patient, accessible by ID. Testing only!
        Returns:
            dict: Patients in the database
        """
        ret_json = {}
        for user in Patient.objects.all():
            ret_json[user.patient_id] = self.convert_to_json(user)
        return ret_json

    def add_patient(self, user_info):
        """
        Adds a new patient into the database.
        Args:
            user_info (dict): Dictionary with the user's info.
        """
        patient = self.get_patient(user_info["patient_id"])
        if patient:
            raise ValueError("The patient is already in the database.")

        p = Patient(patient_id=user_info["patient_id"],
                    attending_email=user_info["attending_email"],
                    user_age=user_info["user_age"],
                    )
        p.save()

    def remove_patient(self, patient_id):
        """
        Removes the patient from the database.
        Args:
            patient_id (str): ID of the patient to remove.

        Returns:
            bool: Whether or not the user was removed.
        """
        removed = False
        # raw won't work for some reason
        for user in Patient.objects.all():
            if str(user.patient_id) == patient_id:
                removed = True
                user.delete()
        return removed

    def get_patient(self, patient_id):
        """
        Finds the patient from the database.
        Args:
            patient_id (str): ID of the patient to remove

        Returns:
            dict: Information of the patient. Returns None if DNE.

        """
        # raw won't work for some weird reason...
        for user in Patient.objects.all():
            if str(user.patient_id) == patient_id:
                return user
        return None

    def add_hr(self, patient_id, heart_rate, timestamp):
        """
        Adds a heart rate and corresponding timestamp to a user.
        Args:
            patient_id: ID of the patient to add hr to.
            heart_rate: New heart rate.
            timestamp: New timestamp.
        """
        user_exists = False
        query = {
            "patient_id": patient_id
        }
        for user in Patient.objects.all():
            if str(user.patient_id) == patient_id:
                user.heart_rates.append(heart_rate)
                user.timestamps.append(timestamp)
                user.save()
                user_exists = True
        return user_exists

    def convert_to_json(self, db_object):
        """
        Converts a database entry into a json object.
        Args:
            db_object: Database entry.

        Returns:
            dict: Dictionary of the database entry.

        """
        patient = {
            "patient_id": db_object.patient_id,
            "attending_email": db_object.attending_email,
            "user_age": db_object.user_age,
            "heart_rates": db_object.heart_rates,
            "timestamps": db_object.timestamps,
        }
        return patient
