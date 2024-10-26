# app/models.py

from flask_login import UserMixin
from datetime import datetime
from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    configurations = db.relationship('Configuration', backref='owner', lazy=True, cascade="all, delete-orphan")
    conversations = db.relationship('Conversation', backref='owner', lazy=True, cascade="all, delete-orphan")
    custom_models = db.relationship('CustomModel', backref='owner', lazy=True, cascade="all, delete-orphan")
    messages = db.relationship('Message', backref='sender', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifies the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Configuration(db.Model):
    __tablename__ = 'configuration'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    inference_count = db.Column(db.Integer, nullable=False, default=18)
    model_order = db.Column(db.Text, nullable=False)  # Stored as JSON string
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    conversations = db.relationship('Conversation', backref='configuration', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Configuration('{self.name}', '{self.inference_count}')"


class Conversation(db.Model):
    __tablename__ = 'conversation'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    configuration_id = db.Column(db.Integer, db.ForeignKey('configuration.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Conversation('{self.title}', '{self.created_at}')"


class Message(db.Model):
    __tablename__ = 'message'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Message('{self.sender.username}', '{self.timestamp}')"


class CustomModel(db.Model):
    __tablename__ = 'custom_model'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Model name
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(200), nullable=False)  # Path to the uploaded model file
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"CustomModel('{self.name}', '{self.uploaded_at}')"
