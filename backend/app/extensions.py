from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

mail = Mail()
limiter = Limiter(key_func=get_remote_address)

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
api = Api(title="Heart Disease API", version="1.0", doc="/api/docs")

bcrypt = Bcrypt()
jwt = JWTManager()
