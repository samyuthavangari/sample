from flask import Flask, request, jsonify
import joblib
import os

app = Flask(__name__)

# Load the trained ML model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "app", "ml", "heart_model.joblib")
model = joblib.load(MODEL_PATH)

@app.route("/")
def home():
    return "Heart Disease Prediction API is running!"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json  # incoming JSON data
        features = data["features"]  # list of input features
        
        # Make prediction
        prediction = model.predict([features])[0]
        return jsonify({"prediction": int(prediction)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
