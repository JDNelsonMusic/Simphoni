# app/__init__.py
from flask import Flask
from flask_wtf import CSRFProtect
from .extensions import db, migrate, login_manager, session
from .celery_app import make_celery, celery
import os
import logging
from logging.handlers import RotatingFileHandler

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # Ensure this path is correct

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    session.init_app(app)  # Initialize Flask-Session
    csrf = CSRFProtect(app)

    # Initialize Celery with app context
    make_celery(app)  # This configures the celery instance

    # Register Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.conversation import conversation_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(conversation_bp)

    # Import models to ensure they are registered
    with app.app_context():
        from . import models

    # Define user_loader here to avoid circular imports
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User  # Import inside function to prevent circular import
        return User.query.get(int(user_id))

    # Set up logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/symphoni.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Symphoni startup')

    # Add context processor to make 'enumerate' available in all templates
    @app.context_processor
    def utility_processor():
        return dict(enumerate=enumerate)

    return app
