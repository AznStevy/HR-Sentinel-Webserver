import motor


class HRMDatabase(object):
    def __init__(self, **kwargs):
        self.db_name = kwargs.get("name", "hrm_database")
        self.db_client = motor.motor_asyncio.AsyncIOMotorClient()
        self.database = self.db_client[self.db_name]  # overall database, not collection
        self.patients = self.database["patients"]

    async def add_patient(self, new_patient):
        pass

    async def remove_patient(self, patient_id):
        pass

    async def get_patient(self, patient_id):
        pass
