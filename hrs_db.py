import motor


class HRMDatabase(object):
    def __init__(self, **kwargs):
        self.db_name = kwargs.get("name", "hrm_database")
        self.db_client = motor.motor_asyncio.AsyncIOMotorClient()
        self.database = self.db_client[self.db_name]  # overall database, not collection
        self.patients = self.database["patients"]

    async def add_patient(self, new_patient):
        """
        Adds patient into the patient collection
        Args:
            new_patient (dict): Dictionary of attributes that describe the patient

        """
        if type(new_patient) != dict:
            raise TypeError("Must pass in type dict")

        # additional checks for attributes
        patient_id = await self._check_patient_id(new_patient)
        user_age = self._check_user_age(new_patient)
        attending_email = self._check_email(new_patient)

        # verified object
        verified_patient = {
            "patient_id": patient_id,
            "user_age": user_age,
            "attending_email": attending_email
        }

        await self.patients.insert_one(verified_patient)

    async def update_patient(self, updated_patient):
        """
        Update the information of an existing patient.
        Args:
            updated_patient (dict): Dictionary of attributes that describe the patient.
        """
        if type(updated_patient) != dict:
            raise TypeError("Must pass in type dict")
        if updated_patient.get("patient_id") is None:
            raise AttributeError("Must contain patient_id")

        # additional checks for attributes
        patient_id = updated_patient.get("patient_id")
        if not await self._check_patient_exists(patient_id):
            raise ValueError("The patient does not exist. Please use add_patient.")

        user_age = self._check_user_age(updated_patient)
        attending_email = self._check_email(updated_patient)

        await self.patients.update_one({"patient_id": patient_id}, {
            "user_age": user_age,
            "attending_email": attending_email
        })

    async def _check_patient_id(self, new_patient):
        """
        Checks if the patient id is valid.
        Args:
            new_patient (dict): New patient who must contain patient_id

        Returns:
            str: The verified patient id.

        """
        if new_patient.get("patient_id") is None:
            raise AttributeError("Must contain patient_id")

        patient_id = new_patient["patient_id"]
        if type(patient_id) != str:
            patient_id = str(patient_id)

        patient_exists = await self._check_patient_exists(patient_id)
        if patient_exists:
            raise ValueError("patient already exists, please use update_patient")

        return patient_id

    async def _check_patient_exists(self, patient_id: str):
        """
        Checks if the patient id exists within the database.
        Args:
            patient_id (str): The patient id that should be tested.

        Returns:
            bool: Whether or not the patient exists.

        """
        found_patient = await self.get_patient(patient_id)
        if found_patient:
            return True
        return False

    def _check_user_age(self, new_patient):
        """
        Checks if the user's age of the object is valid.
        Args:
            new_patient (dict): the new patient that should be tested.

        Returns:
            int: The new patient's age.

        """
        if new_patient.get("user_age") is None:
            raise AttributeError("Must contain user_age")

        user_age = new_patient["user_age"]
        if type(user_age) != int:
            raise TypeError("user_age must be type int")
        if user_age < 0 or user_age > 120:
            raise ValueError("user_age must be between 0 and 120.")
        return user_age

    def _check_email(self, new_patient):
        """
        Checks whether or not the new patient's email is valid.
        Args:
            new_patient: The new patient that should be tested.

        Returns:
            str: The verified email.

        """
        if new_patient.get("attending_email") is None:
            raise AttributeError("Must contain attending_email")

        attending_email = new_patient["attending_email"]
        if type(attending_email) != str:
            attending_email = str(attending_email)
        if "@" not in attending_email:
            raise ValueError("Please enter a valid email address/must contain @")
        return attending_email

    async def remove_patient(self, patient_id: str):
        """
        Removes patient from database based on ID
        Args:
            patient_id (str): The patient that should be removed.

        Returns:
            bool: Whether or not a patient was removed
        """
        patient_exists = await self._check_patient_exists(patient_id)
        if not patient_exists:
            return False

        await self.patients.delete_one({'patient_id': patient_id})
        return True

    async def get_patient(self, patient_id: str):
        """
        Retrieves a patient's information
        Args:
            patient_id (str): The patient that is to be found.

        Returns:
            dict: Patient information from database.

        """
        found_patient = await self.patients.find_one({"patient_id": patient_id})
        return found_patient
