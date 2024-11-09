# app/models.py

from flask_login import UserMixin
from datetime import datetime
from .extensions import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    
    configurations = db.relationship('Configuration', backref='owner', lazy=True)
    conversations = db.relationship('Conversation', backref='owner', lazy=True)
    custom_models = db.relationship('CustomModel', backref='owner', lazy=True)
    personas = db.relationship('Persona', backref='owner', lazy=True)  # Added relationship

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

    def __repr__(self):
        return f"Configuration('{self.name}', '{self.inference_count}')"

class Conversation(db.Model):
    __tablename__ = 'conversation'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    history = db.Column(db.Text, nullable=False)  # Stored as JSON string
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Conversation('{self.title}', '{self.created_at}')"

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

class Persona(db.Model):
    __tablename__ = 'persona'
    
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(100), nullable=True)
    creativity = db.Column(db.Integer, nullable=False, default=5)
    model_name = db.Column(db.String(100), nullable=False, default='llama3.2:3b')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Persona('{self.nickname}', '{self.creativity}', '{self.model_name}')"
