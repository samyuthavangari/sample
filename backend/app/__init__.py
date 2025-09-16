# backend/app/__init__.py
from flask import Flask
from .config import Config
from .resources.health import ns as health_ns
from .resources.predictions import ns as pred_ns
from .resources.documents import ns as doc_ns
from .routes import frontend
from .extensions import db, migrate, api, cors, mail
from .extensions import mail, limiter,bcrypt,jwt
from . import models
from .resources.users import ns as user_ns
from .resources import predictions
#api.add_namespace(predictions.ns, path="/predictions")

api.add_namespace(user_ns, path="/api/users")
api.add_namespace(pred_ns, path="/api/predictions") 

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)
    
    app.register_blueprint(frontend)
    bcrypt.init_app(app)
    jwt.init_app(app)



    # init extensions
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    mail.init_app(app)   
    limiter.init_app(app)


    # IMPORTANT: import models here so Alembic/Flask-Migrate can see them
    # (this registers model classes with SQLAlchemy metadata)
    from . import models

    # register namespaces
    api.add_namespace(health_ns, path='/api')
    api.add_namespace(pred_ns, path='/api')
    api.add_namespace(doc_ns, path='/api')

    return app
