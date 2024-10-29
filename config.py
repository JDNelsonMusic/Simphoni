# config.py

import os
import redis

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    
    # Define the base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Use absolute path for SQLite database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(BASE_DIR, 'symphoni.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.from_url(REDIS_URL)

    # Celery Configuration
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
