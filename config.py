# app/config.py

import os
from redis import Redis

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', '5f5afdfb5d527be1ccfd5a3b56adb2dc')
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'symphoni.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Login
    LOGIN_MESSAGE = "Please log in to access this page."
    LOGIN_MESSAGE_CATEGORY = "info"
    
    # Flask-Session
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_REDIS = Redis(host='localhost', port=6379, db=0)
    SESSION_COOKIE_NAME = 'symphoni_session'
    
    # Celery Configuration
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # Other configurations can be added here
