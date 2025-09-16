# backend/app/config.py
import os
from dotenv import load_dotenv

# load .env from backend/ directory
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(base_dir, ".env"))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///heart.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(base_dir, "app", "uploads")  # optional
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_gmail@gmail.com'
MAIL_PASSWORD = 'your_app_password'  # use Gmail App Password, not your normal password
MAIL_DEFAULT_SENDER = 'your_gmail@gmail.com'
