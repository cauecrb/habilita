from flask import Flask
from .config import Config
from .extensions import db, login_manager
from .auth.routes import auth_bp
from .main.routes import main_bp
from .admin.routes import admin_bp
from .models import User

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app
