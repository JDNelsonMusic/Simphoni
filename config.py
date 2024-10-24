# config.py

import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '5f5afdfb5d527be1ccfd5a3b56adb2dc')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///symphoni.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Session Configuration
    SESSION_TYPE = 'redis'  # Or 'filesystem', 'sqlalchemy', etc.
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_NAME = 'symphoni_session'  # Define a unique session cookie name
    SESSION_REDIS = os.getenv('SESSION_REDIS_URL', 'redis://localhost:6379/0')
