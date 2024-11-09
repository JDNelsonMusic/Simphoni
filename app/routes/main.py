# app/routes/main.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app import db
from app.models import Configuration, CustomModel, Persona
from app.forms import SetupForm, PersonaSetupForm
import json
from werkzeug.utils import secure_filename
import os
import logging
from sqlalchemy import func
from datetime import datetime

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
    recent_activity = []  # Implement if needed
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
        {'name': 'llama3.2:1b', 'display': 'llama3.2:1b'},
        {'name': 'llama3.2:3b', 'display': 'llama3.2:3b'},
        {'name': 'mistral:7b', 'display': 'mistral:7b'},
        {'name': 'mistral-nemo', 'display': 'mistral-nemo'},
        {'name': 'solar-pro', 'display': 'solar-pro'},
        {'name': 'stable-code', 'display': 'stable-code'},
        {'name': 'nous-hermes:34b', 'display': 'nous-hermes:34b'},
        {'name': 'Stable-Diffusion:3.5b', 'display': 'Stable-Diffusion:3.5b'},
        {'name': 'phi3:14b-medium-128k-instruct-fp16', 'display': 'phi3:14b-medium-128k-instruct-fp16'},
        {'name': 'llama3.1:70b', 'display': 'llama3.1:70b'},
        {'name': 'orca-mini:70b', 'display': 'orca-mini:70b'},
        {'name': 'nemotron:70b', 'display': 'nemotron:70b'},
        {'name': 'phi3:medium-128k', 'display': 'phi3:medium-128k'},
        {'name': 'falcon:7b', 'display': 'falcon:7b'},
        {'name': 'wizard-vicuna-uncensored:30b', 'display': 'wizard-vicuna-uncensored:30b'},
        {'name': 'smolm2:135m', 'display': 'smolm2:135m'},
        {'name': 'smolm2:1.7b', 'display': 'smolm2:1.7b'}
    ]

    return render_template(
        'persona_setup.html',
        form=form,
        personas=personas_data,
        available_models=available_models
    )

@main_bp.route('/configuration/view/<int:config_id>', methods=['GET'])
@login_required
def view_configuration(config_id):
    """
    Route to view a specific configuration based on config_id.
    """
    configuration = Configuration.query.filter_by(id=config_id, owner=current_user).first()
    if not configuration:
        flash('Configuration not found.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    # Assuming you have a template named 'view_configuration.html'
    return render_template('view_configuration.html', configuration=configuration)

@main_bp.route('/configuration/edit/<int:config_id>', methods=['GET', 'POST'])
@login_required
def edit_configuration(config_id):
    """
    Route to edit a specific configuration based on config_id.
    """
    configuration = Configuration.query.filter_by(id=config_id, owner=current_user).first()
    if not configuration:
        flash('Configuration not found.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    form = SetupForm(obj=configuration)
    if form.validate_on_submit():
        # Update configuration details
        configuration.name = form.config_name.data.strip()
        configuration.inference_count = int(form.inference_count.data)
        configuration.model_order = form.model_order.data  # Assuming JSON string
        
        try:
            db.session.commit()
            flash('Configuration updated successfully.', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the configuration. Please try again.', 'danger')
            logging.error(f"Error updating configuration: {e}")
            return redirect(request.url)
    
    # Prepopulate form with existing data
    form.config_name.data = configuration.name
    form.inference_count.data = configuration.inference_count
    form.model_order.data = configuration.model_order

    return render_template('edit_configuration.html', form=form, configuration=configuration)

@main_bp.route('/configuration/delete/<int:config_id>', methods=['POST'])
@login_required
def delete_configuration(config_id):
    """
    Route to delete a specific configuration based on config_id.
    """
    configuration = Configuration.query.filter_by(id=config_id, owner=current_user).first()
    if not configuration:
        flash('Configuration not found.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    try:
        db.session.delete(configuration)
        db.session.commit()
        flash('Configuration deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the configuration. Please try again.', 'danger')
        logging.error(f"Error deleting configuration: {e}")
    
    return redirect(url_for('main.dashboard'))

@main_bp.route('/persona_setup', methods=['GET', 'POST'])
@login_required
def persona_setup():
    """
    Route to handle the Persona Setup page.
    Handles both GET (rendering the persona setup form) and POST (processing form submissions).
    """
    form = PersonaSetupForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            personas = []
            for i in range(1, 10):
                nickname = request.form.get(f'nickname_{i}', '').strip()
                creativity = request.form.get(f'creativity_{i}', '5').strip()
                model_name = request.form.get(f'model_name_{i}', 'llama3.2:3b').strip()
                
                # Validate creativity value
                try:
                    creativity = int(creativity)
                    if creativity < 1 or creativity > 9:
                        raise ValueError
                except ValueError:
                    flash(f'Creativity value for Persona {i} must be between 1 and 9.', 'warning')
                    return redirect(request.url)
                
                # Save individual persona
                persona = Persona(
                    nickname=nickname,
                    creativity=creativity,
                    model_name=model_name,
                    owner=current_user
                )
                personas.append(persona)
            
            try:
                # Clear existing personas
                Persona.query.filter_by(owner=current_user).delete()
                # Add new personas
                db.session.add_all(personas)
                db.session.commit()
                flash('Persona Array saved successfully.', 'success')
                return redirect(url_for('main.dashboard'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while saving your personas. Please try again.', 'danger')
                logging.error(f"Error saving personas: {e}")
                return redirect(request.url)
        else:
            flash('Please correct the errors in the form.', 'danger')
    
    # Fetch existing personas or initialize defaults
    existing_personas = Persona.query.filter_by(owner=current_user).order_by(Persona.id).all()
    personas_data = []
    for i in range(1, 10):
        if i-1 < len(existing_personas):
            persona = existing_personas[i-1]
            personas_data.append({
                'nickname': persona.nickname,
                'creativity': persona.creativity,
                'model_name': persona.model_name
            })
        else:
            # Defaults: model_name='llama3.2:3b', creativity=5, nickname=''
            personas_data.append({
                'nickname': '',
                'creativity': 5,
                'model_name': 'llama3.2:3b'
            })
    
    # List of available models from Ollama (17 models)
    available_models = [
        {'name': 'llama3.2:1b', 'display': 'llama3.2:1b'},
        {'name': 'llama3.2:3b', 'display': 'llama3.2:3b'},
        {'name': 'mistral:7b', 'display': 'mistral:7b'},
        {'name': 'mistral-nemo', 'display': 'mistral-nemo'},
        {'name': 'solar-pro', 'display': 'solar-pro'},
        {'name': 'stable-code', 'display': 'stable-code'},
        {'name': 'nous-hermes:34b', 'display': 'nous-hermes:34b'},
        {'name': 'Stable-Diffusion:3.5b', 'display': 'Stable-Diffusion:3.5b'},
        {'name': 'phi3:14b-medium-128k-instruct-fp16', 'display': 'phi3:14b-medium-128k-instruct-fp16'},
        {'name': 'llama3.1:70b', 'display': 'llama3.1:70b'},
        {'name': 'orca-mini:70b', 'display': 'orca-mini:70b'},
        {'name': 'nemotron:70b', 'display': 'nemotron:70b'},
        {'name': 'phi3:medium-128k', 'display': 'phi3:medium-128k'},
        {'name': 'falcon:7b', 'display': 'falcon:7b'},
        {'name': 'wizard-vicuna-uncensored:30b', 'display': 'wizard-vicuna-uncensored:30b'},
        {'name': 'smolm2:135m', 'display': 'smolm2:135m'},
        {'name': 'smolm2:1.7b', 'display': 'smolm2:1.7b'}
    ]

    return render_template(
        'persona_setup.html',
        form=form,
        personas=personas_data,
        available_models=available_models
    )

@main_bp.route('/my_arrays')
@login_required
def my_arrays():
    """Route for My Arrays page."""
    # Implement the logic for My Arrays
    return render_template('my_arrays.html')

@main_bp.route('/past_is_threads')
@login_required
def past_is_threads():
    """Route for Past IS-Threads page."""
    # Implement the logic for Past IS-Threads
    return render_template('past_is_threads.html')

@main_bp.route('/is_setup')
@login_required
def is_setup():
    """Route for IS-Setup page."""
    # Implement the logic for IS-Setup
    return render_template('is_setup.html')

@main_bp.route('/tools')
@login_required
def tools():
    """Route for Tools page."""
    # Implement the logic for Tools
    return render_template('tools.html')

@main_bp.route('/settings')
@login_required
def settings():
    """Route for Settings page."""
    # Implement the logic for Settings
    return render_template('settings.html')
