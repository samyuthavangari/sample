# backend/app/models.py
from .extensions import db
from datetime import datetime
from .extensions import db
from datetime import datetime



class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default="patient")  # patient or doctor
    
        # new fields
    role = db.Column(db.String(20), default="patient")  # patient or doctor
    is_verified = db.Column(db.Boolean, default=False)  # 🚨 verify email
    failed_attempts = db.Column(db.Integer, default=0)  # 🚨 login security
    locked_until = db.Column(db.DateTime, nullable=True)


    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email}
    def set_password(self, password, bcrypt):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password, bcrypt):
        return bcrypt.check_password_hash(self.password_hash, password)

class Prediction(db.Model):
    __tablename__ = "prediction"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    input_data = db.Column(db.JSON, nullable=False)   # flexible storage
    result = db.Column(db.String(64), nullable=False)
    probability = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("predictions", lazy=True))

class MedicalDocument(db.Model):
    __tablename__ = "medical_document"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    filename = db.Column(db.String(256), nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("documents", lazy=True))


#Notes:

#db.JSON works fine with SQLite via SQLAlchemy (it stores JSON text). 
# If your SQLAlchemy version complains, change db.JSON → db.Text and store json.dumps(...)/json.loads(...) when writing/reading.