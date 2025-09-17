from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models import Prediction
from ..ml import model_loader
import numpy as np
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
import datetime
import traceback

ns = Namespace('predictions', description='Heart disease predictions')

# --- Response schemas ---
prediction_output = ns.model('PredictionOutput', {
    "id": fields.Integer,
    "prediction": fields.Integer,
    "probability": fields.Float,
    "risk": fields.String,
})

prediction_history = ns.model('PredictionHistory', {
    "id": fields.Integer,
    "result": fields.String,
    "probability": fields.Float,
    "input_data": fields.Raw,
    "created_at": fields.String
})

# ---------------- JSON-based prediction API ----------------
@ns.route('/')
class PredictionResource(Resource):
    @ns.expect(ns.model('PredictionInput', {
        "age": fields.Integer(required=True),
        "sex": fields.Integer(required=True),
        "cp": fields.Integer(required=True),
        "trestbps": fields.Integer(required=True),
        "chol": fields.Integer(required=True),
        "fbs": fields.Integer(required=True),
        "restecg": fields.Integer(required=True),
        "thalach": fields.Integer(required=True),
        "exang": fields.Integer(required=True),
        "oldpeak": fields.Float(required=True),
        "slope": fields.Integer(required=True),
        "ca": fields.Integer(required=True),
        "thal": fields.Integer(required=True),
        "model": fields.String(default="logreg")
    }))
    @ns.marshal_with(prediction_output)
    def post(self):
        """Predict via raw JSON payload"""
        try:
            data = ns.payload

            X = np.array([[data['age'], data['sex'], data['cp'], data['trestbps'],
                           data['chol'], data['fbs'], data['restecg'], data['thalach'],
                           data['exang'], data['oldpeak'], data['slope'], data['ca'],
                           data['thal']]])

            model = model_loader.load_model(data.get("model", "logreg"))

            pred = int(model.predict(X)[0])
            prob = float(model.predict_proba(X)[0][1])
            risk = "High Risk" if pred == 1 else "Low Risk"

            new_pred = Prediction(
                user_id=None,
                input_data=data,
                result=risk,
                probability=prob,
                created_at=datetime.datetime.utcnow()
            )
            db.session.add(new_pred)
            db.session.commit()

            return {"id": new_pred.id, "prediction": pred, "probability": prob, "risk": risk}

        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}, 500


# ---------------- Prediction History ----------------
@ns.route('/history')
class PredictionHistoryResource(Resource):
    @ns.marshal_list_with(prediction_history)
    @jwt_required()
    def get(self):
        """Fetch all past predictions for logged-in user"""
        user_id = get_jwt_identity()
        preds = Prediction.query.filter_by(user_id=user_id).order_by(Prediction.created_at.desc()).all()
        return preds


# ---------------- Upload + Form-based prediction ----------------
@ns.route("/upload")
class UploadPrediction(Resource):
    @jwt_required()
    def post(self):
        try:
            user_id = get_jwt_identity()

            # 📂 Optional file (not yet used in ML, but can be saved if needed)
            document = request.files.get("document")

            # 📋 Collect form fields
            form = request.form
            required_fields = [
                "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
                "thalach", "exang", "oldpeak", "slope", "ca", "thal"
            ]

            # ✅ Validate required fields
            for field in required_fields:
                if field not in form or form[field] == "":
                    return {"error": f"Missing field: {field}"}, 400

            # ✅ Convert to numeric safely
            try:
                X = np.array([[int(form["age"]), int(form["sex"]), int(form["cp"]),
                               int(form["trestbps"]), int(form["chol"]), int(form["fbs"]),
                               int(form["restecg"]), int(form["thalach"]),
                               int(form["exang"]), float(form["oldpeak"]),
                               int(form["slope"]), int(form["ca"]), int(form["thal"])]])
            except ValueError as ve:
                return {"error": f"Invalid input format: {str(ve)}"}, 400

            # ✅ Choose model (default: logreg)
            model_name = form.get("model", "logreg")
            model = model_loader.load_model(model_name)

            pred = int(model.predict(X)[0])
            prob = float(model.predict_proba(X)[0][1])
            risk = "High Risk" if pred == 1 else "Low Risk"

            # ✅ Save prediction in DB
            prediction = Prediction(
                user_id=user_id,
                result=risk,
                probability=prob,
                input_data=form.to_dict(),
                created_at=datetime.datetime.utcnow()
            )
            db.session.add(prediction)
            db.session.commit()

            return {
                "id": prediction.id,
                "result": risk,
                "probability": prob,
                "created_at": prediction.created_at.strftime("%Y-%m-%d %H:%M")
            }, 200

        except Exception as e:
            print("🔥 UploadPrediction ERROR:", str(e))
            traceback.print_exc()
            return {"error": f"Internal Server Error: {str(e)}"}, 500
