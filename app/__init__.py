from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # Registering blueprints
    from .routes import bp as clans_bp
    app.register_blueprint(clans_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()  # Create database tables for our data models

    return app