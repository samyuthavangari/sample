from flask import Blueprint, render_template

frontend = Blueprint("frontend", __name__)

@frontend.route("/")
def home():
    return render_template("base.html")

@frontend.route("/login")
def login_page():
    return render_template("login.html")

@frontend.route("/register")
def register():
    return render_template("register.html")


@frontend.route("/predict")
def predict():
    return render_template("predict.html")

@frontend.route("/profile")
def profile():
    return render_template("profile.html")

@frontend.route("/result")
def result():
    return render_template("result.html")

@frontend.route("/upload")
def upload():
    return render_template("upload.html")
