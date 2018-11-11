from flask import Flask, jsonify
import hrs_db
import uvloop
import aiohttp
import asyncio

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = Flask("heart_rate_sentinel_server")  # some unique identifier


class HRMSentinelAPI(object):
    def __init__(self):
        self.database = hrs_db()

    @app.route("/api/status/<patient_id>", methods=["GET"])
    async def get_status(self, name):
        pass

    @app.route("/api/heart_rate/<patient_id>", methods=["GET"])
    async def get_heart_rate(self, patient_id):
        pass

    @app.route("/api/heart_rate/average/<patient_id>", methods=["GET"])
    async def get_average(self, patient_id):
        pass

    @app.route("/api/heart_rate/internal_average", methods=["GET"])
    async def get_internal_average(self):
        pass

    @app.route("/api/new_patient", methods=["POST"])
    async def post_new_patient(self):
        pass

    @app.route("/api/heart_rate", methods=["POST"])
    async def post_heart_rate(self):
        pass


if __name__ == "__main__":
    app.run(host="127.0.0.1")
