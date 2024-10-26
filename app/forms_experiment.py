# app/forms.py

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField,
    IntegerField, TextAreaField
)
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
)
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=2, max=20)
    ])
    email = StringField('Email', validators=[
        DataRequired(), Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password')
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired()
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SetupForm(FlaskForm):
    config_name = StringField('Configuration Name', validators=[
        DataRequired(), Length(min=2, max=100)
    ])
    inference_count = IntegerField('Number of Inferences', validators=[
        DataRequired(), NumberRange(min=1, max=100)
    ])
    model_order = TextAreaField('Model Order (JSON)', validators=[
        DataRequired()
    ])
    description = TextAreaField('Description', validators=[
        Length(max=500)
    ])
    submit = SubmitField('Save Configuration')

class ConversationForm(FlaskForm):
    title = StringField('Conversation Title', validators=[
        DataRequired(), Length(max=150)
    ])
    message = TextAreaField('Initial Message', validators=[
        DataRequired(), Length(max=1000)
    ])
    submit = SubmitField('Start Conversation')

class MessageForm(FlaskForm):
    message = TextAreaField('Your Message', validators=[
        DataRequired(), Length(max=1000)
    ])
    submit = SubmitField('Send')




# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
import json

#class RegistrationForm(FlaskForm):
    #username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    #email = StringField('Email', validators=[DataRequired(), Email()])
    #password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    #confirm_password = PasswordField('Confirm Password',
                                     #validators=[DataRequired(), EqualTo('password')])
    #submit = SubmitField('Register')

#class LoginForm(FlaskForm):
    #username = StringField('Username', validators=[DataRequired()])
    #password = PasswordField('Password', validators=[DataRequired()])
    #remember = BooleanField('Remember Me')
    #submit = SubmitField('Login')

#class SetupForm(FlaskForm):
    #config_name = StringField('Configuration Name', validators=[DataRequired(), Length(min=2, max=100)])
    #inference_count = IntegerField('Number of Inferences', validators=[DataRequired(), NumberRange(min=1, max=100)])
    #model_order = StringField('Model Order', validators=[DataRequired()])  # Stored as JSON string
    #submit = SubmitField('Save Configuration')
