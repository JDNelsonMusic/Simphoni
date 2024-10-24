Absolutely, Jon! Let's create a fully functional version of your Symphoni application that you can copy and paste into your project directory. This version will incorporate all the lessons learned so far, ensure compatibility with Python 3.12, and avoid using virtual environments as per your preference.

Overview of the Steps
Prepare the Environment:

Ensure Python 3.12 is installed.
Install Redis on your machine.
Set Up the Project Files:

Replace existing files with the provided versions.
Ensure all necessary directories and files are correctly placed.
Install Dependencies:

Use pip to install all required packages listed in requirements.txt.
Initialize the Database:

Run database migrations to set up the SQLite database.
Start Redis and Celery:

Ensure Redis server is running.
Start the Celery worker for asynchronous task processing.
Run the Flask Application:

Launch the Flask app and access the GUI pages.
1. Prepare the Environment
a. Ensure Python 3.12 is Installed
First, verify that Python 3.12 is installed on your system:

bash
Copy code
python3.12 --version
If Not Installed:
Using Homebrew:
bash
Copy code
brew install python@3.12
Verify Installation:
bash
Copy code
python3.12 --version
Expected Output:
Copy code
Python 3.12.x
b. Install Redis
Redis is required for Celery to function properly.

Using Homebrew:

bash
Copy code
brew install redis
Start Redis Server:

bash
Copy code
brew services start redis
Verify Redis is Running:

bash
Copy code
redis-cli ping
Expected Response:
Copy code
PONG
2. Set Up the Project Files
Below is the complete set of files you need to create or replace in your project directory. Ensure that each file is placed in the correct location as per the project structure.

Project Structure
arduino
Copy code
Symphoni/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── extensions.py
│   ├── forms.py
│   ├── tasks.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── main.py
│   │   └── conversation.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── setup.html
│   │   ├── dashboard.html
│   │   ├── upload_model.html
│   │   ├── end_conversation.html
│   │   ├── omnicall.html
│   │   ├── conversation.html
│   │   └── conversation_start.html
│   └── static/
│       ├── css/
│       │   └── styles.css
│       ├── js/
│       │   └── scripts.js
│       └── images/
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   ├── versions/
│   │   └── 74735f061110_initial_migration.py
│   └── __pycache__/
├── migrations_backup/
│   └── README
├── instance/
│   └── symphoni.db
├── celery_worker.py
├── config.py
├── manage.py
├── run.py
├── requirements.txt
├── dump.rdb
└── README.md
a. requirements.txt
Create or replace the requirements.txt file with the following content:

plaintext
Copy code
Flask==2.3.3
Flask-Session==0.4.0
Flask-Login==0.6.2
Flask-Migrate==4.0.4
Flask-SQLAlchemy==3.0.0
Celery==5.2.7
redis==5.0.0
Werkzeug==2.3.6
python-dotenv==0.21.1
Flask-WTF==1.2.1
WTForms==3.0.1
markupsafe==3.0.1
Note: Ensure that you use exact versions to maintain compatibility.

b. config.py
Create or replace config.py with the following content:

python
Copy code
# config.py

import os
from dotenv import load_dotenv
from markupsafe import Markup

# Load environment variables from a .env file if present
load_dotenv()

class Config:
    # Security Key for Flask-WTF CSRF Protection and Session Management
    SECRET_KEY = os.environ.get('SECRET_KEY') or '5f5afdfb5d527be1ccfd5a3b56adb2dc'
    WTF_CSRF_ENABLED = True  # Ensure this is True or remove it since it's True by default

    # SQLAlchemy Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/symphoni.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'

    # Flask-Session Configuration to Use Redis
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_REDIS = os.environ.get('SESSION_REDIS_URL') or 'redis://localhost:6379/0'

    # Maximum Allowed Payload to Prevent Large File Uploads (16 MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Additional Configurations (Add as Needed)
    # Example: MAIL_SERVER, MAIL_PORT, etc.
c. app/__init__.py
Create or replace app/__init__.py with the following content:

python
Copy code
# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from flask_login import LoginManager
from flask_wtf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
sess = Session()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # Ensure your config is correctly set

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)  # Initialize CSRF protection
    sess.init_app(app)

    # Register Blueprints
    from app.routes import main_bp, auth_bp, conversation_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(conversation_bp)

    return app
d. app/models.py
Create or replace app/models.py with the following content:

python
Copy code
# app/models.py

from .extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    configurations = db.relationship('Configuration', backref='owner', lazy=True)
    conversations = db.relationship('Conversation', backref='owner', lazy=True)
    custom_models = db.relationship('CustomModel', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Configuration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    inference_count = db.Column(db.Integer, nullable=False, default=18)
    model_order = db.Column(db.Text, nullable=False)  # Stored as JSON string
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Configuration('{self.name}', '{self.inference_count}')"

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    history = db.Column(db.Text, nullable=False)  # Stored as JSON string
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"Conversation('{self.title}', '{self.created_at}')"

class CustomModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Model name
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(200), nullable=False)  # Path to the uploaded model file
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"CustomModel('{self.name}', '{self.uploaded_at}')"
e. app/extensions.py
Create or replace app/extensions.py with the following content:

python
Copy code
# app/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Redirect to 'auth.login' when login is required
login_manager.login_message_category = 'info'
f. app/forms.py
Create app/forms.py to handle form classes. Here's a basic implementation based on your routes:

python
Copy code
# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, RadioField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # Custom validators to check for existing username and email
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SetupForm(FlaskForm):
    config_name = StringField('Configuration Name', validators=[DataRequired(), Length(max=100)])
    inference_count = RadioField('Number of Inferences', choices=[('9', '9'), ('18', '18')], default='18', validators=[DataRequired()])
    model_order = HiddenField('Model Order', validators=[DataRequired()])
    submit = SubmitField('Save Configuration')
g. app/tasks.py
Create or replace app/tasks.py with the following content:

python
Copy code
# app/tasks.py

from app import create_app, db
from app.models import Conversation
from celery import Celery
import subprocess
from datetime import datetime
import logging

# Initialize Celery with the Flask app context
def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

app = create_app()
celery = make_celery(app)

@celery.task(bind=True)
def process_model_inference(self, model_name, prompt, model_options):
    """
    Celery task to process model inference asynchronously.
    """
    cmd = ['ollama', 'run']

    # Add model-specific options if provided
    if model_options:
        for key, value in model_options.items():
            cmd.extend([f'--{key}', str(value)])

    # Add the model name
    cmd.append(model_name)

    # Separator for the prompt
    cmd.append('--')

    # Add the prompt
    cmd.append(prompt)

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=120)  # 2-minute timeout

        if process.returncode != 0:
            return {'success': False, 'error': stderr.strip()}
        else:
            return {'success': True, 'response': stdout.strip()}
    except subprocess.TimeoutExpired:
        process.kill()
        return {'success': False, 'error': 'Model inference timed out.'}
    except Exception as e:
        logging.exception("Exception during model inference.")
        return {'success': False, 'error': str(e)}
h. app/routes/auth.py
Create or replace app/routes/auth.py with the following content:

python
Copy code
# app/routes/auth.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.forms import RegistrationForm, LoginForm
from app.models import User
from app import db
from flask_login import login_user, logout_user, login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Registration logic here
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Login logic here
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))
i. app/routes/main.py
Create or replace app/routes/main.py with the following content:

python
Copy code
# app/routes/main.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Configuration, CustomModel
from app.forms import SetupForm
import json
from werkzeug.utils import secure_filename
import os
import logging

main_bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'json', 'yaml', 'yml'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def home():
    """Home page route. Redirects to dashboard if user is authenticated."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('home.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard route."""
    configurations = Configuration.query.filter_by(owner=current_user).all()
    custom_models = CustomModel.query.filter_by(owner=current_user).all()
    conversations = current_user.conversations  # Assuming relationship is set
    recent_activity = []  # Placeholder for recent activity
    return render_template('dashboard.html', configurations=configurations, custom_models=custom_models, conversations=conversations, recent_activity=recent_activity)

@main_bp.route('/upload_model', methods=['GET', 'POST'])
@login_required
def upload_model():
    """
    Route to handle uploading of custom models.
    Handles both GET (rendering the upload form) and POST (processing the uploaded file).
    """
    if request.method == 'POST':
        if 'model_file' not in request.files:
            flash('No file part.', 'warning')
            return redirect(request.url)
        file = request.files['model_file']
        if file.filename == '':
            flash('No selected file.', 'warning')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = os.path.join('app', 'uploaded_models')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            # Create a new CustomModel entry
            custom_model = CustomModel(
                name=request.form.get('model_name', '').strip(),
                description=request.form.get('model_description', '').strip(),
                file_path=file_path,
                owner=current_user
            )
            try:
                db.session.add(custom_model)
                db.session.commit()
                flash('Custom model uploaded successfully.', 'success')
                return redirect(url_for('main.setup'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while uploading the model. Please try again.', 'danger')
                logging.error(f"Error uploading model: {e}")
                return redirect(request.url)
        else:
            flash('Invalid file type. Allowed types are: json, yaml, yml.', 'warning')
            return redirect(request.url)
    else:
        return render_template('upload_model.html')

@main_bp.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    """
    Route to handle the setup configuration.
    Utilizes Flask-WTF's SetupForm for secure form handling and CSRF protection.
    """
    form = SetupForm()
    if form.validate_on_submit():
        # Retrieve form data using Flask-WTF's form object
        models_info = {}
        inference_count = form.inference_count.data
        model_order = form.model_order.data  # JSON string
        try:
            model_order = json.loads(model_order)
        except json.JSONDecodeError:
            flash('Invalid model order configuration.', 'danger')
            return redirect(request.url)

        # Process each slot's data
        for slot_num in range(1, 10):
            slot_id = f'slot_{slot_num}'
            nickname = request.form.get(f'nickname_{slot_id}', '').strip()
            role = request.form.get(f'role_{slot_id}', '').strip()
            model_name = request.form.get(f'model_name_{slot_id}', '').strip()
            instruct = request.form.get(f'instruct_{slot_id}', '').strip()
            context_window = request.form.get(f'context_window_{slot_id}', '2048').strip()
            options = request.form.get(f'options_{slot_id}', '{}').strip()

            # Validate and parse options
            try:
                options = json.loads(options) if options else {}
            except json.JSONDecodeError:
                flash(f"Invalid JSON for options in {slot_id}.", 'warning')
                options = {}

            models_info[slot_id] = {
                'nickname': nickname,
                'role': role,
                'model_name': model_name,
                'instruct': instruct,
                'context_window': int(context_window),
                'options': options
            }

        # Create a new Configuration entry
        config_name = form.config_name.data.strip()
        new_config = Configuration(
            name=config_name,
            inference_count=int(inference_count),
            model_order=json.dumps(model_order),
            owner=current_user
        )

        try:
            db.session.add(new_config)
            db.session.commit()
            # Store models_info in session or handle as needed
            session['models_info'] = models_info
            flash('Setup configurations saved successfully.', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while saving your configuration. Please try again.', 'danger')
            logging.error(f"Error saving configuration: {e}")
            return redirect(request.url)
    else:
        if request.method == 'POST':
            flash('Please correct the errors in the form.', 'danger')

    # Fetch the latest configuration or initialize default
    latest_config = Configuration.query.filter_by(owner=current_user).order_by(Configuration.created_at.desc()).first()
    if latest_config:
        model_order = json.loads(latest_config.model_order)
        # Fetch custom models uploaded by the user
        custom_models = CustomModel.query.filter_by(owner=current_user).all()

        # Initialize models_info with existing slots if available
        models_info = {}
        for slot_num in range(1, 10):
            slot_id = f'slot_{slot_num}'
            models_info[slot_id] = {
                'nickname': '',
                'role': '',
                'model_name': '',
                'instruct': '',
                'context_window': 2048,
                'options': {}
            }
    else:
        # Initialize with empty slots numbered 1-9 and default model_order
        models_info = {}
        model_order = [f'slot_{i}' for i in range(1, 10)]  # Default order
        custom_models = []

    # List of available models with exact Ollama names
    available_models = [
        {
            'name': 'llama3.2:1b',
            'nickname': 'The Speedster',
            'size': '1 billion parameters',
            'description': 'Ideal for tasks that require quick responses without sacrificing too much accuracy. Great for day-to-day text summarization, quick instructions, or short dialogues.'
        },
        {
            'name': 'llama3.2:3b',
            'nickname': 'The Balanced One',
            'size': '3 billion parameters',
            'description': 'A well-rounded model for text generation, summarization, and dialogue, providing a balance between speed and complexity.'
        },
        {
            'name': 'falcon-7b',
            'nickname': 'The Broad Thinker',
            'size': '7 billion parameters',
            'description': 'Versatile and can be applied to a wide range of language tasks, from creative writing to technical assistance.'
        },
        {
            'name': 'mike/mistral',
            'nickname': 'The Contextual Genius',
            'size': '12 billion parameters, 128K context window',
            'description': 'Excels in large-context tasks, such as analyzing long documents or holding extended conversations.'
        },
        {
            'name': 'Solar-Pro',
            'nickname': 'The Tech Guru',
            'size': '22 billion parameters',
            'description': 'Exceptional performance in generating code, technical documents, and complex instructions.'
        },
        {
            'name': 'llama3.1:70B',
            'nickname': 'The Mastermind',
            'size': '70 billion parameters',
            'description': 'Suitable for tasks requiring intricate problem-solving, scientific research, or high-level creative writing.'
        },
        {
            'name': 'nous-hermes2:34b',
            'nickname': 'The Scholar',
            'size': '34 billion parameters',
            'description': 'Built for detailed scientific and philosophical discourse, ideal for educational and specialized fields.'
        },
        {
            'name': 'wizard-vicuna-uncensored:30b',
            'nickname': 'The Unchained Wizard',
            'size': '30 billion parameters',
            'description': 'Uncensored version suitable for creative freedom or unrestricted text generation.'
        },
        {
            'name': 'stable-code',
            'nickname': 'The Code Scribe',
            'size': '3 billion parameters',
            'description': 'Excels in helping developers write cleaner and more efficient code.'
        }
    ]

    return render_template(
        'setup.html',
        form=form,  # Pass the form object here
        models_info=models_info,
        available_models=available_models,
        custom_models=custom_models,
        model_order=model_order
    )
j. app/routes/conversation.py
Create or replace app/routes/conversation.py with the following content:

python
Copy code
# app/routes/conversation.py

from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    request, jsonify, send_file, session
)
from flask_login import login_required, current_user
from app import db, celery
from app.models import Conversation, Configuration
from datetime import datetime
import json
from werkzeug.utils import secure_filename
import os
import logging

conversation_bp = Blueprint('conversation_bp', __name__)

@celery.task
def process_model_inference(model_name, prompt, model_options):
    """
    Celery task to process model inference asynchronously.
    """
    cmd = ['ollama', 'run']

    # Add model-specific options if provided
    if model_options:
        for key, value in model_options.items():
            cmd.extend([f'--{key}', str(value)])

    # Add the model name
    cmd.append(model_name)

    # Separator for the prompt
    cmd.append('--')

    # Add the prompt
    cmd.append(prompt)

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=120)  # 2-minute timeout

        if process.returncode != 0:
            return {'success': False, 'error': stderr.strip()}
        else:
            return {'success': True, 'response': stdout.strip()}
    except subprocess.TimeoutExpired:
        process.kill()
        return {'success': False, 'error': 'Model inference timed out.'}
    except Exception as e:
        logging.exception("Exception during model inference.")
        return {'success': False, 'error': str(e)}

def construct_prompt(model_key, conversation_history, models_info, conversation_goal):
    """
    Constructs the prompt for the model based on the role, instruct statements,
    conversation history, and goal.
    """
    model_info = models_info.get(model_key, {})
    role = model_info.get('role', '')
    instruct = model_info.get('instruct', '')
    context_window = model_info.get('context_window', 2048)  # Default context window

    prompt = ''
    if role:
        prompt += f"Role: {role}\n"
    if instruct:
        prompt += f"Instruct: {instruct}\n"
    if conversation_goal:
        prompt += f"Conversation Goal: {conversation_goal}\n"

    # Include conversation history within context window (rough estimation: 1 token ≈ 4 characters)
    max_characters = context_window * 4
    history_text = ''
    for entry in reversed(conversation_history):
        entry_text = f"{entry['speaker']} [{entry['timestamp']}]: {entry['message']}\n"
        if len(history_text) + len(entry_text) < max_characters:
            history_text = entry_text + history_text
        else:
            break  # Exceeds context window

    prompt += history_text
    prompt += f"{model_key}:"
    return prompt

@conversation_bp.route('/conversation', methods=['GET', 'POST'])
@login_required
def conversation():
    if request.method == 'POST':
        return handle_post_request()
    else:
        return handle_get_request()

def handle_post_request():
    """
    Handles POST requests to the /conversation route.
    This includes starting a new conversation or handling OmniCall input.
    """
    if 'conversation_id' not in session:
        # Handle initial message and conversation goal
        conversation_goal = request.form.get('conversation_goal', '').strip()
        initial_message = request.form.get('initial_message', '').strip()
        if not initial_message:
            flash('Initial message is required.', 'warning')
            return render_template('conversation_start.html')

        # Create a new Conversation entry
        new_conversation = Conversation(
            title=request.form.get(
                'conversation_title',
                f"{current_user.username}'s Conversation"
            ),
            history=json.dumps([{
                'speaker': 'User',
                'message': initial_message,
                'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }]),
            owner=current_user
        )
        try:
            db.session.add(new_conversation)
            db.session.commit()
            session['conversation_id'] = new_conversation.id
            session['conversation_goal'] = conversation_goal

            # Initialize models_info in session
            latest_config = Configuration.query.filter_by(
                owner=current_user
            ).order_by(Configuration.created_at.desc()).first()
            if latest_config:
                model_order = json.loads(latest_config.model_order)
                session['model_order'] = model_order

                # Fetch models_info from session or initialize
                if 'models_info' not in session:
                    models_info = {}
                    for slot_num in range(1, 10):
                        slot_id = f'slot_{slot_num}'
                        models_info[slot_id] = {
                            'nickname': '',
                            'role': '',
                            'model_name': '',
                            'instruct': '',
                            'context_window': 2048,
                            'options': {}
                        }
                    session['models_info'] = models_info
            else:
                flash('No configuration found. Please set up your conversation.', 'warning')
                return redirect(url_for('main.setup'))

            logging.debug(f"Initialized conversation ID: {new_conversation.id}")
            logging.debug(f"Conversation goal: {conversation_goal}")
            logging.debug(f"Model order: {model_order}")
            logging.debug(f"Models info: {session.get('models_info')}")

            flash('Conversation started successfully.', 'success')
            return redirect(url_for('conversation_bp.conversation'))
        except Exception as e:
            db.session.rollback()
            logging.exception("Error creating new conversation.")
            flash('An error occurred while starting the conversation. Please try again.', 'danger')
            return render_template('conversation_start.html')
    else:
        # Handle OmniCall input
        user_input = request.form.get('user_input', '').strip()
        if user_input:
            # Fetch the conversation
            conversation = Conversation.query.get(session.get('conversation_id'))
            if not conversation:
                flash('Conversation not found.', 'danger')
                return redirect(url_for('main.home'))

            # Update conversation history
            history = json.loads(conversation.history)
            history.append({
                'speaker': 'OmniCall',
                'message': user_input,
                'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            })
            conversation.history = json.dumps(history)
            db.session.commit()

            logging.debug(f"Added OmniCall input to conversation ID: {conversation.id}")

            flash('Input added to conversation.', 'success')
            return redirect(url_for('conversation_bp.conversation'))
        else:
            flash('Input is required.', 'warning')
            conversation = Conversation.query.get(session.get('conversation_id'))
            if conversation:
                history = json.loads(conversation.history)
                return render_template('omnicall.html', conversation_history=history)
            else:
                flash('Conversation not found.', 'danger')
                return redirect(url_for('main.home'))

def handle_get_request():
    """
    Handles GET requests to the /conversation route.
    This includes displaying the conversation and processing model responses.
    """
    try:
        if 'conversation_id' not in session:
            # Render initial message and conversation goal input form
            return render_template('conversation_start.html')
        else:
            # Fetch the conversation
            conversation = Conversation.query.get(session.get('conversation_id'))
            if not conversation:
                flash('Conversation not found.', 'danger')
                return redirect(url_for('main.home'))

            history = json.loads(conversation.history)
            conversation_goal = session.get('conversation_goal', '')
            latest_config = Configuration.query.filter_by(
                owner=current_user
            ).order_by(Configuration.created_at.desc()).first()
            if not latest_config:
                flash('No configuration found. Please set up your conversation.', 'warning')
                return redirect(url_for('main.setup'))

            model_order = session.get('model_order', json.loads(latest_config.model_order))
            inference_count = latest_config.inference_count

            # Determine the next model in the sequence
            current_turn = len(history) - 1  # Subtracting the initial user message
            if current_turn >= inference_count:
                flash('Conversation has reached its maximum number of inferences.', 'info')
                return redirect(url_for('conversation_bp.end_conversation'))

            # Validate model_order
            if not isinstance(model_order, list) or len(model_order) == 0:
                logging.error("model_order is empty or not a list.")
                flash("Configuration error: No models available for conversation.", 'danger')
                return redirect(url_for('main.setup'))

            current_model_key = model_order[current_turn % len(model_order)]

            logging.debug(f"Model order: {model_order}")
            logging.debug(f"Current turn: {current_turn}")
            logging.debug(f"Current model key: {current_model_key}")

            # Check if current_model_key is OmniCall
            if current_model_key.lower() == 'omnicall':
                return render_template('omnicall.html', conversation_history=history)

            # Fetch models_info from session
            models_info = session.get('models_info', {})
            if not models_info:
                flash('Model configurations not found. Please set up your conversation.', 'warning')
                return redirect(url_for('main.setup'))

            model_info = models_info.get(current_model_key, {})
            model_name = model_info.get('model_name', '')
            instruct = model_info.get('instruct', '')
            context_window = model_info.get('context_window', 2048)
            options = model_info.get('options', {})

            if not model_name:
                flash(f"Model '{current_model_key}' is not configured.", 'danger')
                return redirect(url_for('conversation_bp.conversation'))

            # Construct the prompt
            prompt = construct_prompt(current_model_key, history, models_info, conversation_goal)
            logging.debug(f"Constructed prompt: {prompt}")

            # Enqueue the model inference task
            task = process_model_inference.delay(model_name, prompt, options)

            # Wait for the task to complete (for simplicity; consider using WebSockets for real-time updates)
            result = task.get(timeout=120)  # 2-minute timeout

            if result['success']:
                response = result['response']
                # Update conversation history
                history.append({
                    'speaker': model_info.get('nickname') or model_info.get('role') or current_model_key,
                    'message': response,
                    'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                })
                conversation.history = json.dumps(history)
                db.session.commit()

                logging.debug(f"Added model response to conversation ID: {conversation.id}")

                flash(f"Response from {model_info.get('nickname') or model_info.get('role') or current_model_key}.", 'success')
            else:
                flash(f"Error from {model_info.get('nickname') or model_info.get('role') or current_model_key}: {result['error']}", 'danger')

            return redirect(url_for('conversation_bp.conversation'))
    except ZeroDivisionError:
        logging.exception("ZeroDivisionError encountered in /conversation route.")
        flash("An internal error occurred. Please contact support.", 'danger')
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        logging.exception("Unexpected error during GET request in /conversation route.")
        flash("An unexpected error occurred. Please try again.", "danger")
        return redirect(url_for('main.dashboard'))

@conversation_bp.route('/end_conversation', methods=['GET', 'POST'])
@login_required
def end_conversation():
    """
    Handles the end of a conversation, allowing users to save the conversation history to a file.
    """
    if 'conversation_id' not in session:
        flash('No active conversation to end.', 'warning')
        return redirect(url_for('main.home'))
    
    conversation = Conversation.query.get(session.get('conversation_id'))
    if not conversation:
        flash('Conversation not found.', 'danger')
        return redirect(url_for('main.home'))

    history = json.loads(conversation.history)

    if request.method == 'POST':
        # Save conversation to a file
        file_name = request.form.get('file_name', 'conversation.txt').strip()
        if not file_name:
            file_name = 'conversation.txt'
        file_name = secure_filename(file_name)

        try:
            with open(file_name, 'w') as f:
                for entry in history:
                    f.write(f"{entry['speaker']} [{entry['timestamp']}]: {entry['message']}\n")
            logging.debug(f"Conversation ID {conversation.id} saved to {file_name}")
            return send_file(file_name, as_attachment=True)
        except Exception as e:
            logging.exception("Error saving conversation to file.")
            flash(f"Error saving conversation: {e}", 'danger')
            return render_template('end_conversation.html', conversation_history=history)
    else:
        return render_template('end_conversation.html', conversation_history=history)
k. app/routes/__init__.py
Create or replace app/routes/__init__.py with the following content:

python
Copy code
# app/routes/__init__.py

from .main import main_bp
from .auth import auth_bp
from .conversation import conversation_bp
l. app/forms.py
You already have app/forms.py from step f. Ensure it's included in the app/ directory.

m. app/templates/base.html
Create or replace app/templates/base.html with the following content:

html
Copy code
<!-- app/templates/base.html -->

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Symphoni</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
</head>
<body class="bg-dark text-light">
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-purple mb-4">
        <div class="container-fluid">
            <a class="navbar-brand" href="{{ url_for('main.home') }}">Symphoni</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    {% if current_user.is_authenticated %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('main.setup') }}">Setup</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('conversation_bp.conversation') }}">Conversation</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('auth.logout') }}">Logout</a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('auth.login') }}">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('auth.register') }}">Register</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Flash Messages -->
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>

    <!-- Main Content -->
    <div class="container">
        {% block content %}{% endblock %}
    </div>

    <!-- Bootstrap JS and dependencies -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom JS -->
    <script src="{{ url_for('static', filename='js/scripts.js') }}"></script>
</body>
</html>
n. app/templates/home.html
Create or replace app/templates/home.html with the following content:

html
Copy code
<!-- app/templates/home.html -->

{% extends "base.html" %}
{% block content %}
<div class="text-center">
    <h1>Welcome to Symphoni</h1>
    <p>Orchestrate multi-model conversations with ease.</p>
    {% if not current_user.is_authenticated %}
        <a href="{{ url_for('auth.login') }}" class="btn btn-primary">Login</a>
        <a href="{{ url_for('auth.register') }}" class="btn btn-secondary">Register</a>
    {% else %}
        <a href="{{ url_for('main.setup') }}" class="btn btn-primary">Setup Conversation</a>
        <a href="{{ url_for('conversation_bp.conversation') }}" class="btn btn-secondary">Start Conversation</a>
    {% endif %}
</div>
{% endblock %}
o. app/templates/login.html
Create or replace app/templates/login.html with the following content:

html
Copy code
<!-- app/templates/login.html -->

{% extends "base.html" %}
{% block content %}
  <div class="row justify-content-center">
      <div class="col-md-6">
          <h2>Login</h2>
          <form method="post" action="{{ url_for('auth.login') }}">
            {{ form.hidden_tag() }}
            <div class="mb-3">
              {{ form.username.label(class="form-label") }}
              {{ form.username(class="form-control", placeholder="Enter your username") }}
              {% if form.username.errors %}
                  <div class="text-danger">
                      {% for error in form.username.errors %}
                          <small>{{ error }}</small>
                      {% endfor %}
                  </div>
              {% endif %}
            </div>
            <div class="mb-3">
              {{ form.password.label(class="form-label") }}
              {{ form.password(class="form-control", placeholder="Enter your password") }}
              {% if form.password.errors %}
                  <div class="text-danger">
                      {% for error in form.password.errors %}
                          <small>{{ error }}</small>
                      {% endfor %}
                  </div>
              {% endif %}
            </div>
            <div class="mb-3">
              {{ form.submit(class="btn btn-primary") }}
            </div>
          </form>
      </div>
  </div>
{% endblock %}
p. app/templates/register.html
Create or replace app/templates/register.html with the following content:

html
Copy code
<!-- app/templates/register.html -->

{% extends "base.html" %}
{% block content %}
  <div class="row justify-content-center">
      <div class="col-md-6">
          <h2>Register</h2>
          <form method="post" action="{{ url_for('auth.register') }}">
            {{ form.hidden_tag() }}
            <div class="mb-3">
              {{ form.username.label(class="form-label") }}
              {{ form.username(class="form-control", placeholder="Choose a username") }}
              {% if form.username.errors %}
                  <div class="text-danger">
                      {% for error in form.username.errors %}
                          <small>{{ error }}</small>
                      {% endfor %}
                  </div>
              {% endif %}
            </div>
            <div class="mb-3">
              {{ form.email.label(class="form-label") }}
              {{ form.email(class="form-control", placeholder="Enter your email") }}
              {% if form.email.errors %}
                  <div class="text-danger">
                      {% for error in form.email.errors %}
                          <small>{{ error }}</small>
                      {% endfor %}
                  </div>
              {% endif %}
            </div>
            <div class="mb-3">
              {{ form.password.label(class="form-label") }}
              {{ form.password(class="form-control", placeholder="Create a password") }}
              {% if form.password.errors %}
                  <div class="text-danger">
                      {% for error in form.password.errors %}
                          <small>{{ error }}</small>
                      {% endfor %}
                  </div>
              {% endif %}
            </div>
            <div class="mb-3">
              {{ form.confirm_password.label(class="form-label") }}
              {{ form.confirm_password(class="form-control", placeholder="Confirm your password") }}
              {% if form.confirm_password.errors %}
                  <div class="text-danger">
                      {% for error in form.confirm_password.errors %}
                          <small>{{ error }}</small>
                      {% endfor %}
                  </div>
              {% endif %}
            </div>
            <div class="mb-3">
              {{ form.submit(class="btn btn-primary") }}
            </div>
          </form>
      </div>
  </div>
{% endblock %}
q. app/templates/setup.html
Create or replace app/templates/setup.html with the following content:

html
Copy code
<!-- app/templates/setup.html -->

{% extends "base.html" %}
{% block content %}
<div class="container my-4">
    <h2>Setup Your Conversation</h2>
    <form method="POST" action="{{ url_for('main.setup') }}">
        {{ form.hidden_tag() }} <!-- Renders hidden fields like CSRF token -->

        <!-- Configuration Name -->
        <div class="mb-3">
            {{ form.config_name.label(class="form-label") }}
            {{ form.config_name(class="form-control", placeholder="Enter a name for this configuration") }}
            {% if form.config_name.errors %}
                <div class="text-danger">
                    {% for error in form.config_name.errors %}
                        <small>{{ error }}</small>
                    {% endfor %}
                </div>
            {% endif %}
        </div>

        <!-- Number of Inferences -->
        <div class="mb-4">
            {{ form.inference_count.label(class="form-label") }}
            <div class="d-flex gap-3">
                {% for subfield in form.inference_count %}
                    <div class="form-check">
                        {{ subfield(class="form-check-input") }}
                        {{ subfield.label(class="form-check-label") }}
                    </div>
                {% endfor %}
            </div>
            {% if form.inference_count.errors %}
                <div class="text-danger">
                    {% for error in form.inference_count.errors %}
                        <small>{{ error }}</small>
                    {% endfor %}
                </div>
            {% endif %}
        </div>

        <!-- Available Functions -->
        <div class="mb-4">
            <h4>Available Functions</h4>
            <div id="available-functions" class="d-flex flex-wrap gap-2">
                {% for slot_num in range(1,10) %}
                    {% set slot_id = 'slot_' ~ slot_num|string %}
                    <div class="available-function badge bg-secondary p-2 draggable" draggable="true" data-slot-id="{{ slot_id }}">
                        {% if models_info[slot_id]['nickname'] %}
                            {{ models_info[slot_id]['nickname'] }}
                        {% else %}
                            Slot{{ slot_num }}
                        {% endif %}
                    </div>
                {% endfor %}
                <!-- OmniCall Function -->
                <div class="available-function badge bg-info p-2 draggable" draggable="true" data-function="omnicall">
                    OmniCall
                </div>
            </div>
        </div>

        <!-- Arrange Model Sequence -->
        <div class="mb-4">
            <h4>Arrange Model Sequence:</h4>
            <p>Drag and drop to arrange the order of model slots. You can insert OmniCall multiple times.</p>
            <ul id="model-order" class="list-group mb-3">
                {% if model_order and model_order|length > 0 %}
                    {% for idx, slot in enumerate(model_order, start=1) %}
                        <li class="list-group-item d-flex align-items-center" draggable="true">
                            <span class="badge bg-primary me-2">{{ idx }}</span>
                            <span class="flex-grow-1 slot-content">{{ slot }}</span>
                            <button type="button" class="btn btn-sm btn-danger remove-slot">Remove</button>
                        </li>
                    {% endfor %}
                {% else %}
                    <!-- Default slots if no model_order is set -->
                    {% for slot_num in range(1,19) %}
                        <li class="list-group-item d-flex align-items-center" draggable="true">
                            <span class="badge bg-primary me-2">{{ slot_num }}</span>
                            <span class="flex-grow-1 slot-content"></span>
                            <button type="button" class="btn btn-sm btn-danger remove-slot">Remove</button>
                        </li>
                    {% endfor %}
                {% endif %}
            </ul>
            {{ form.model_order(id='model_order') }} <!-- Hidden input for model_order -->
        </div>

        <!-- Save Configuration Button -->
        <button type="submit" class="btn btn-primary">{{ form.submit.label.text }}</button>
    </form>
</div>

<!-- Drag-and-Drop Script -->
<script>
    document.addEventListener('DOMContentLoaded', () => {
        const inferenceRadios = document.querySelectorAll('input[name="inference_count"]');
        const modelOrderList = document.getElementById('model-order');
        const modelOrderInput = document.getElementById('model_order'); // Ensure this matches the form field's id
        const availableFunctions = document.getElementById('available-functions');

        // Function to update the number of slots based on selected inferences
        function updateSlots(count) {
            modelOrderList.innerHTML = ''; // Clear existing slots
            for (let i = 1; i <= count; i++) {
                const li = document.createElement('li');
                li.classList.add('list-group-item', 'd-flex', 'align-items-center');
                li.setAttribute('draggable', 'true');

                const badge = document.createElement('span');
                badge.classList.add('badge', 'bg-primary', 'me-2');
                badge.textContent = i;

                const slotContent = document.createElement('span');
                slotContent.classList.add('flex-grow-1', 'slot-content');
                slotContent.textContent = ''; // Blank by default

                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.classList.add('btn', 'btn-sm', 'btn-danger', 'remove-slot');
                removeBtn.textContent = 'Remove';

                li.appendChild(badge);
                li.appendChild(slotContent);
                li.appendChild(removeBtn);

                modelOrderList.appendChild(li);
            }
            addSlotEventListeners(); // Re-add event listeners
            updateModelOrderInput(); // Update hidden input
        }

        // Function to handle inference count changes
        inferenceRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                const selectedCount = parseInt(e.target.value);
                updateSlots(selectedCount);
            });
        });

        // Function to add event listeners to slots
        function addSlotEventListeners() {
            const slots = document.querySelectorAll('#model-order .list-group-item');
            slots.forEach(slot => {
                // Drag events
                slot.addEventListener('dragstart', handleDragStart, false);
                slot.addEventListener('dragover', handleDragOver, false);
                slot.addEventListener('drop', handleDrop, false);
                slot.addEventListener('dragend', handleDragEnd, false);

                // Remove button event
                const removeBtn = slot.querySelector('.remove-slot');
                removeBtn.addEventListener('click', () => {
                    slot.remove();
                    updateModelOrderInput();
                });
            });
        }

        // Drag and Drop Handlers
        let dragSrcEl = null;

        function handleDragStart(e) {
            dragSrcEl = this;
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', this.querySelector('.slot-content').textContent);
            this.classList.add('dragging');
        }

        function handleDragOver(e) {
            if (e.preventDefault) {
                e.preventDefault(); // Necessary to allow drop
            }
            e.dataTransfer.dropEffect = 'move';
            return false;
        }

        function handleDrop(e) {
            if (e.stopPropagation) {
                e.stopPropagation(); // Prevent default action
            }

            if (dragSrcEl !== this) {
                const draggedData = e.dataTransfer.getData('text/plain');
                const targetContent = this.querySelector('.slot-content');

                // Swap the content
                const temp = targetContent.textContent;
                targetContent.textContent = draggedData;
                dragSrcEl.querySelector('.slot-content').textContent = temp;

                updateModelOrderInput();
            }
            return false;
        }

        function handleDragEnd(e) {
            this.classList.remove('dragging');
        }

        // Handle dragging from Available Functions to Slots
        availableFunctions.querySelectorAll('.draggable').forEach(func => {
            func.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', func.dataset.slotId || func.dataset.function || '');
                e.dataTransfer.effectAllowed = 'copyMove';
            });
        });

        modelOrderList.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        modelOrderList.addEventListener('drop', (e) => {
            e.preventDefault();
            const data = e.dataTransfer.getData('text/plain');
            const target = e.target.closest('.list-group-item');
            if (target) {
                const slotContent = target.querySelector('.slot-content');
                if (data.startsWith('slot_')) {
                    // It's a model slot from Available Functions
                    const funcElement = availableFunctions.querySelector(`.available-function[data-slot-id="${data}"]`);
                    const funcName = funcElement ? funcElement.textContent.trim() : 'Unknown Function';
                    slotContent.textContent = funcName;
                } else if (data === 'omnicall') {
                    // It's OmniCall
                    slotContent.textContent = 'OmniCall';
                }
                updateModelOrderInput();
            }
        });

        // Function to update the hidden input for model_order
        function updateModelOrderInput() {
            const slots = modelOrderList.querySelectorAll('.list-group-item .slot-content');
            const order = Array.from(slots).map(slot => slot.textContent.trim()).filter(name => name !== '');
            modelOrderInput.value = JSON.stringify(order);
        }

        // Add event listeners to nickname inputs to update Available Functions in real-time
        const nicknameInputs = document.querySelectorAll('input[name^="nickname_slot_"]');
        nicknameInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                const slotId = e.target.name.split('_').pop(); // e.g., '1' from 'nickname_slot_1'
                const availableFunc = availableFunctions.querySelector(`.available-function[data-slot-id="slot_${slotId}"]`);
                if (availableFunc) {
                    const newNickname = e.target.value.trim();
                    availableFunc.textContent = newNickname !== '' ? newNickname : `Slot${slotId}`;
                }
            });
        });

        // Initial Setup based on existing model_order or default to selected inferences
        const initialInference = document.querySelector('input[name="inference_count"]:checked').value;
        updateSlots(parseInt(initialInference));
    });
</script>
{% endblock %}
q. app/templates/dashboard.html
Create or replace app/templates/dashboard.html with the following content:

html
Copy code
<!-- app/templates/dashboard.html -->

{% extends "base.html" %}

{% block content %}
<div class="container my-4">
    <!-- Welcome Section -->
    <div class="row mb-4">
        <div class="col">
            <h1 class="mb-3">Welcome, {{ current_user.username }}!</h1>
            <p class="lead">Manage your configurations, custom models, and conversations all in one place.</p>
        </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row mb-4">
        <!-- Configurations Card -->
        <div class="col-md-4">
            <div class="card text-bg-primary mb-3">
                <div class="card-body">
                    <h5 class="card-title">Configurations</h5>
                    <p class="card-text display-4">{{ configurations | length }}</p>
                </div>
            </div>
        </div>
        <!-- Custom Models Card -->
        <div class="col-md-4">
            <div class="card text-bg-success mb-3">
                <div class="card-body">
                    <h5 class="card-title">Custom Models</h5>
                    <p class="card-text display-4">{{ custom_models | length }}</p>
                </div>
            </div>
        </div>
        <!-- Conversations Card -->
        <div class="col-md-4">
            <div class="card text-bg-warning mb-3">
                <div class="card-body">
                    <h5 class="card-title">Conversations</h5>
                    <p class="card-text display-4">{{ conversations | length }}</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Configurations Management -->
    <div class="row mb-5">
        <div class="col">
            <h3>Your Configurations</h3>
            <a href="{{ url_for('main.setup') }}" class="btn btn-primary mb-3">Create New Configuration</a>
            {% if configurations %}
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th scope="col">Configuration Name</th>
                                <th scope="col">Inference Count</th>
                                <th scope="col">Created At</th>
                                <th scope="col">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for config in configurations %}
                                <tr>
                                    <td>{{ config.name }}</td>
                                    <td>{{ config.inference_count }}</td>
                                    <td>{{ config.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                                    <td>
                                        <a href="{{ url_for('main.view_configuration', config_id=config.id) }}" class="btn btn-sm btn-info">View</a>
                                        <a href="{{ url_for('main.edit_configuration', config_id=config.id) }}" class="btn btn-sm btn-secondary">Edit</a>
                                        <form action="{{ url_for('main.delete_configuration', config_id=config.id) }}" method="POST" class="d-inline" onsubmit="return confirm('Are you sure you want to delete this configuration?');">
                                            <button type="submit" class="btn btn-sm btn-danger">Delete</button>
                                        </form>
                                    </td>
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p>You have no configurations yet. <a href="{{ url_for('main.setup') }}">Create one now.</a></p>
            {% endif %}
        </div>
    </div>

    <!-- Custom Models Management -->
    <div class="row mb-5">
        <div class="col">
            <h3>Your Custom Models</h3>
            <a href="{{ url_for('main.upload_model') }}" class="btn btn-success mb-3">Upload New Custom Model</a>
            {% if custom_models %}
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th scope="col">Model Name</th>
                                <th scope="col">Description</th>
                                <th scope="col">Uploaded At</th>
                                <th scope="col">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for model in custom_models %}
                                <tr>
                                    <td>{{ model.name }}</td>
                                    <td>{{ model.description }}</td>
                                    <td>{{ model.uploaded_at.strftime('%Y-%m-%d %H:%M') }}</td>
                                    <td>
                                        <a href="{{ url_for('main.view_custom_model', model_id=model.id) }}" class="btn btn-sm btn-info">View</a>
                                        <form action="{{ url_for('main.delete_custom_model', model_id=model.id) }}" method="POST" class="d-inline" onsubmit="return confirm('Are you sure you want to delete this custom model?');">
                                            <button type="submit" class="btn btn-sm btn-danger">Delete</button>
                                        </form>
                                    </td>
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <p>You have no custom models uploaded. <a href="{{ url_for('main.upload_model') }}">Upload one now.</a></p>
            {% endif %}
        </div>
    </div>

    <!-- Conversations Overview -->
    <div class="row mb-5">
        <div class="col">
            <h3>Your Conversations</h3>
            <a href="{{ url_for('conversation_bp.conversation') }}" class="btn btn-warning mb-3">Start New Conversation</a>
            {% if conversations %}
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th scope="col">Conversation Title</th>
                                <th scope="col">Created At</th>
                                <th scope="col">Last Updated</th>
                                <th scope="col">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for convo in conversations %}
                                <tr>
                                    <td>{{ convo.title }}</td>
                                    <td>{{ convo.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                                    <td>{{ convo.updated_at.strftime('%Y-%m-%d %H:%M') }}</td>
                                    <td>
                                        <a href="{{ url_for('conversation_bp.view_conversation', convo_id=convo.id) }}" class="btn btn-sm btn-info">View</a>
                                        <form action="{{ url_for('conversation_bp.delete_conversation', convo_id=convo.id) }}" method="POST" class="d-inline" onsubmit="return confirm('Are you sure you want to delete this conversation?');">
                                            <button type="submit" class="btn btn-sm btn-danger">Delete</button>
                                        </form>
                                    </td>
                                </tr>
                            {% endfor %}
                        </tbody
