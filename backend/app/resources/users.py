from flask_restx import Namespace, Resource, fields
from flask import request
from ..extensions import db, bcrypt, mail
from ..models import User
from flask_jwt_extended import (
    create_access_token, jwt_required,
    get_jwt_identity, get_jwt
)
from flask_mail import Message
from email_validator import validate_email, EmailNotValidError
from datetime import timedelta
from ..utils.auth import role_required   # our custom role decorator
from ..models import User, Prediction
from ..extensions import limiter
from flask import request
from app import db
from app.models import User, Document, Prediction   # adjust to your actual models



ns = Namespace("users", description="User Registration and Authentication")

# ---------- Models ----------
register_model = ns.model("Register", {
    "username": fields.String(required=True),
    "email": fields.String(required=True),
    "password": fields.String(required=True)
})

login_model = ns.model("Login", {
    "email": fields.String(required=True),
    "password": fields.String(required=True)
})

reset_model = ns.model("ResetPassword", {
    "new_password": fields.String(required=True)
})

# ---------- Endpoints ----------

@ns.route("/register")
class Register(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return {"error": "Missing JSON body"}, 400

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        # check if user exists
        if User.query.filter_by(email=data["email"]).first():
            return {"error": "Email already registered"}, 400

        user = User(username=data["username"], email=data["email"])
        user.set_password(data["password"], bcrypt)
        db.session.add(user)
        db.session.commit()

        # generate verification token (24h expiry)
        token = create_access_token(
            identity={"id": user.id, "role": user.role},
            expires_delta=timedelta(hours=24)
        )

        # send verification email
        msg = Message(
            subject="Verify your HeartShield account",
            recipients=[user.email],
            body=f"Click link to verify: http://127.0.0.1:5000/verify?token={token}"
        )
        mail.send(msg)

        return {"message": "Registered! Check your email to verify."}

@ns.route("/login")
class Login(Resource):
    def post(self):
        data = request.get_json()
        identifier = data.get("username") or data.get("email")  # accept both
        password = data.get("password")

        user = User.query.filter(
            (User.email == identifier) | (User.username == identifier)
        ).first()

        if not user or not user.check_password(password, bcrypt):
            return {"error": "Invalid credentials"}, 401

        access_token = create_access_token(identity={"id": user.id, "role": user.role})
        return {"access_token": access_token, "message": "Login successful!"}


#@ns.route("/login")
#class Login(Resource):
   # decorators = [limiter.limit("5 per minute")]  # 🚨 rate limit

    #def post(self):
        #data = request.json
        #user = User.query.filter_by(email=data["email"]).first()
       # if not user:
            #return {"error": "Invalid credentials"}, 401

      #  # 🚨 check lockout
      #  if user.locked_until and user.locked_until > datetime.utcnow():
         #   return {"error": "Account locked. Try again later."}, 403

      #  if not bcrypt.check_password_hash(user.password_hash, data["password"]):
           # user.failed_attempts += 1
           # if user.failed_attempts >= 5:  # 5 wrong tries
              #  user.locked_until = datetime.utcnow() + timedelta(minutes=15)
              #  user.failed_attempts = 0
           # db.session.commit()
           # return {"error": "Invalid credentials"}, 401

        # 🚨 check email verification
       # if not user.is_verified:
          #  return {"error": "Please verify your email first"}, 403

        # reset counters on success
       # user.failed_attempts = 0
       # user.locked_until = None
       # db.session.commit()

       # token = create_access_token(identity={"id": user.id, "role": user.role})
        #return {"access_token": token}



@ns.route("/forgot-password")
class ForgotPassword(Resource):
    decorators = [limiter.limit("3 per minute")]  # 🚨 prevent abuse
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data["email"]).first()
        if not user:
            return {"error": "Email not registered"}, 404

        reset_token = create_access_token(
            identity={"id": user.id, "role": user.role},
            expires_delta=timedelta(minutes=15)
        )

        msg = Message(
            subject="Password Reset - Heart Shield",
            recipients=[user.email],
            body=f"Click the link to reset your password: http://127.0.0.1:5000/reset-password?token={reset_token}"
        )
        mail.send(msg)

        return {"message": "Password reset email sent!"}, 200


@ns.route("/reset-password")
class ResetPassword(Resource):
    @ns.expect(reset_model)
    @jwt_required()
    def post(self):
        identity = get_jwt_identity()
        user = User.query.get(identity["id"])
        data = request.get_json()

        if not user:
            return {"error": "User not found"}, 404

        user.set_password(data["new_password"], bcrypt)
        db.session.commit()

        return {"message": "Password updated successfully!"}, 200
    
@ns.route("/verify")
class Verify(Resource):
    @jwt_required()
    def get(self):
        identity = get_jwt_identity()
        user = User.query.get(identity["id"])
        if not user:
            return {"error": "User not found"}, 404

        user.is_verified = True
        db.session.commit()
        return {"message": "Email verified successfully!"}    


# ---------- Role-Based Dashboards ----------
@ns.route("/doctor-dashboard")
class DoctorDashboard(Resource):
    @role_required("doctor")
    def get(self):
        return {"message": "Welcome doctor!"}


@ns.route("/patient-dashboard")
class PatientDashboard(Resource):
    @role_required("patient")
    def get(self):
        return {"message": "Welcome patient!"}
    
@ns.route("/profile")
class UserProfile(Resource):
    @jwt_required()
    def get(self):
        identity = get_jwt_identity()   # returns {"id": ..., "role": ...}
        user = User.query.get(identity["id"])

        if not user:
            return {"error": "User not found"}, 404
        
          # Documents uploaded by this user
        docs = Document.query.filter_by(user_id=user.id).all()
        docs_data = [{
            "id": d.id,
            "filename": d.filename,
            "uploaded_at": d.uploaded_at.strftime("%Y-%m-%d %H:%M")
        } for d in docs]

        # get past predictions
        predictions = Prediction.query.filter_by(user_id=user.id).all()
        history = [
            {
                "id": p.id,
                "result": p.result,
                "probability": p.probability,
                "created_at": p.created_at.strftime("%Y-%m-%d %H:%M")
            }
            for p in predictions
        ]

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "predictions": history
        }