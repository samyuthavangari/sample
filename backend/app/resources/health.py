# backend/app/resources/health.py
from flask_restx import Namespace, Resource

# create a namespace for health
ns = Namespace('health', description='Health check endpoint')

@ns.route('/')
class HealthCheck(Resource):
    def get(self):
        return {"status": "ok", "message": "Heart Disease API is running!"}, 200
