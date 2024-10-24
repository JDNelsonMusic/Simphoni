# app/routes/main.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app import db
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
        # Add more models as needed
    ]

    return render_template(
        'setup.html',
        form=form,
        models_info=models_info,
        model_order=model_order,
        available_models=available_models,
        custom_models=custom_models
        # Removed enumerate=enumerate since it's now available via context processor
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
