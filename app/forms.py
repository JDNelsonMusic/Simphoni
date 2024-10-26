# app/forms.py

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    IntegerField,
    TextAreaField
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
    NumberRange
)
from .models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6)]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Custom validator to check if the username is already taken."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        """Custom validator to check if the email is already registered."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class SetupForm(FlaskForm):
    config_name = StringField(
        'Configuration Name',
        validators=[DataRequired(), Length(min=2, max=100)]
    )
    inference_count = IntegerField(
        'Number of Inferences',
        validators=[DataRequired(), NumberRange(min=1, max=100)]
    )
    model_order = TextAreaField(
        'Model Order',
        validators=[DataRequired()]
    )  # Changed to TextAreaField for better JSON input handling
    submit = SubmitField('Save Configuration')

    def validate_model_order(self, model_order):
        """Custom validator to ensure that model_order is valid JSON."""
        import json
        try:
            json.loads(model_order.data)
        except json.JSONDecodeError:
            raise ValidationError('Model order must be a valid JSON string.')


class ConversationForm(FlaskForm):
    title = StringField(
        'Conversation Title',
        validators=[DataRequired(), Length(min=2, max=150)]
    )
    initial_message = TextAreaField(
        'Initial Message',
        validators=[DataRequired(), Length(min=1)]
    )
    submit = SubmitField('Start Conversation')


class MessageForm(FlaskForm):
    message = TextAreaField(
        'Message',
        validators=[DataRequired(), Length(min=1)]
    )
    submit = SubmitField('Send Message')
