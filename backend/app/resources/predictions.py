from flask_restx import Namespace, Resource, fields
from ..extensions import db
from ..models import Prediction
from ..ml import model_loader
import numpy as np
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request


ns = Namespace('predictions', description='Heart disease predictions')

# Request schema (already defined)
prediction_input = ns.model('PredictionInput', {
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
    "model": fields.String(default="logreg", description="Choose: logreg, rf, svm, nn")
})

# Response schema for single prediction
prediction_output = ns.model('PredictionOutput', {
    "id": fields.Integer,
    "prediction": fields.Integer,
    "probability": fields.Float,
    "risk": fields.String,
})

# Response schema for history
prediction_history = ns.model('PredictionHistory', {
    "id": fields.Integer,
    "result": fields.String,
    "probability": fields.Float,
    "input_data": fields.Raw,  # full JSON input
    "created_at": fields.String
})

@ns.route('/')
class PredictionResource(Resource):
    @ns.expect(prediction_input)
    @ns.marshal_with(prediction_output)
    def post(self):
        try:
            data = ns.payload

            # Prepare input
            X = np.array([[data['age'], data['sex'], data['cp'], data['trestbps'],
                           data['chol'], data['fbs'], data['restecg'], data['thalach'],
                           data['exang'], data['oldpeak'], data['slope'], data['ca'],
                           data['thal']]])

            # Load chosen model
            model_name = data.get("model", "logreg")
            model = model_loader.load_model(model_name)

            pred = int(model.predict(X)[0])
            prob = float(model.predict_proba(X)[0][1])
            risk = "High Risk" if pred == 1 else "Low Risk"

            # Save to DB
            new_pred = Prediction(
                user_id=None,
                input_data=data,
                result=risk,
                probability=prob
            )
            db.session.add(new_pred)
            db.session.commit()

            return {"id": new_pred.id, "prediction": pred, "probability": prob, "risk": risk}

        except Exception as e:
            return {"error": str(e)}, 500


@ns.route('/history')
class PredictionHistoryResource(Resource):
    @ns.marshal_list_with(prediction_history)
    def get(self):
        """Fetch all past predictions"""
        preds = Prediction.query.order_by(Prediction.created_at.desc()).all()
        return preds


@ns.route("/upload")
class UploadPrediction(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()

        # ✅ Get uploaded file (optional - not used yet)
        file = request.files.get("document")

        # ✅ Extract form fields
        try:
            age = int(request.form.get("age"))
            sex = int(request.form.get("sex"))
            cp = int(request.form.get("cp"))
            trestbps = int(request.form.get("trestbps"))
            chol = int(request.form.get("chol"))
            fbs = int(request.form.get("fbs"))
            restecg = int(request.form.get("restecg"))
            thalach = int(request.form.get("thalach"))
            exang = int(request.form.get("exang"))
            oldpeak = float(request.form.get("oldpeak"))
            slope = int(request.form.get("slope"))
            ca = int(request.form.get("ca"))
            thal = int(request.form.get("thal"))
        except (TypeError, ValueError):
            return {"error": "Missing or invalid input fields"}, 400

        # ✅ Build feature vector (exactly 13 fields in correct order)
        X = np.array([[age, sex, cp, trestbps, chol, fbs,
                       restecg, thalach, exang, oldpeak, slope, ca, thal]])

        # ✅ Load model & predict
        model_name = request.form.get("model", "logreg")  # allow model choice
        model = model_loader.load_model(model_name)

        try:
            pred = int(model.predict(X)[0])
            prob = float(model.predict_proba(X)[0][1])  # probability of class 1
            risk = "High Risk" if pred == 1 else "Low Risk"
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}, 500

        # ✅ Save to DB
        prediction = Prediction(
            user_id=user_id,
            result=risk,
            probability=prob,
            input_data=request.form.to_dict(),
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

