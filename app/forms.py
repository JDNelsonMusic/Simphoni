# app/forms.py

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    IntegerField,
    TextAreaField,
    FileField  # Imported FileField
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
    NumberRange
)
import json

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SetupForm(FlaskForm):
    config_name = StringField('Configuration Name', validators=[DataRequired(), Length(min=2, max=100)])
    inference_count = IntegerField('Number of Inferences', validators=[DataRequired(), NumberRange(min=1, max=100)])
    model_order = StringField('Model Order', validators=[DataRequired()])  # Stored as JSON string
    submit = SubmitField('Save Configuration')

class TriviaForm(FlaskForm):
    answer = StringField('Your Answer', validators=[DataRequired()])
    submit = SubmitField('Submit Answer')

class UploadToolForm(FlaskForm):
    tool_file = FileField('Upload Python Tool', validators=[DataRequired()])  # Added FileField
    submit = SubmitField('Upload Tool')
