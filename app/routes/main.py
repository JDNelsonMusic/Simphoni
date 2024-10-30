# app/routes/main.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app import db
from app.models import Configuration, CustomModel, Conversation
from app.forms import SetupForm, TriviaForm, UploadToolForm
import json
from werkzeug.utils import secure_filename
import os
import logging
from sqlalchemy import func
from datetime import datetime
import subprocess  # Ensure this line is present
import sys         # <-- Add this line

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

@main_bp.route('/analytics')
@login_required
def analytics():
    """Route to display analytics on the dashboard."""
    
    # Configurations Over Time
    config_data = db.session.query(
        func.date(Configuration.created_at).label('date'),
        func.count(Configuration.id).label('count')
    ).filter_by(owner=current_user).group_by(func.date(Configuration.created_at)).order_by(func.date(Configuration.created_at)).all()
    
    config_dates = [record.date.strftime('%Y-%m-%d') for record in config_data]
    config_counts = [record.count for record in config_data]
    
    # Custom Models Distribution
    model_data = db.session.query(
        CustomModel.name,
        func.count(CustomModel.id).label('count')
    ).filter_by(owner=current_user).group_by(CustomModel.name).all()
    
    model_names = [record.name for record in model_data]
    model_counts = [record.count for record in model_data]
    
    # Conversations Over Time
    convo_data = db.session.query(
        func.date(Conversation.created_at).label('date'),
        func.count(Conversation.id).label('count')
    ).filter_by(owner=current_user).group_by(func.date(Conversation.created_at)).order_by(func.date(Conversation.created_at)).all()
    
    convo_dates = [record.date.strftime('%Y-%m-%d') for record in convo_data]
    convo_counts = [record.count for record in convo_data]
    
    return render_template(
        'main/analytics.html',
        config_dates=config_dates,
        config_counts=config_counts,
        model_names=model_names,
        model_counts=model_counts,
        convo_dates=convo_dates,
        convo_counts=convo_counts
    )

@main_bp.route('/trivia', methods=['GET', 'POST'])
@login_required
def trivia():
    """
    Route to display the AI Trivia Game.
    Utilizes Flask-WTF's TriviaForm for secure form handling and CSRF protection.
    """
    form = TriviaForm()
    if form.validate_on_submit():
        user_answer = form.answer.data.strip().lower()
        correct_answer = session.get('correct_answer', '').lower()
        
        if user_answer == correct_answer:
            flash('Correct! Well done.', 'success')
        else:
            flash(f'Incorrect. The correct answer was: {session.get("correct_answer")}', 'danger')
        
        # Redirect to get a new question
        return redirect(url_for('main.trivia'))
    
    # Generate a trivia question
    question, answer = generate_trivia_question()
    session['correct_answer'] = answer  # Store the correct answer in session
    
    return render_template('main/trivia.html', form=form, question=question)

def generate_trivia_question():
    """
    Generates a simple trivia question.
    Returns a tuple of (question, answer).
    """
    # For simplicity, we'll use a predefined list of questions.
    trivia_questions = [
        ("What does AI stand for?", "Artificial Intelligence"),
        ("Who is known as the father of computers?", "Charles Babbage"),
        ("What programming language is primarily used for web development?", "JavaScript"),
        ("In which year was the Python programming language released?", "1991"),
        ("What does HTTP stand for?", "HyperText Transfer Protocol"),
    ]
    
    import random
    question, answer = random.choice(trivia_questions)
    return question, answer

@main_bp.route('/tools')
@login_required
def tools():
    """
    Route to display the list of available Python tools.
    """
    tools_directory = os.path.join(os.getcwd(), 'pygame_py_files')
    if not os.path.exists(tools_directory):
        os.makedirs(tools_directory)
    
    # List all .py files in the tools_directory
    tool_files = [f for f in os.listdir(tools_directory) if f.endswith('.py')]
    
    # Remove the .py extension for display purposes
    tool_names = [os.path.splitext(f)[0] for f in tool_files]
    
    return render_template('tools.html', tools=tool_names)

@main_bp.route('/run_tool/<tool_name>')
@login_required
def run_tool(tool_name):
    """
    Route to execute the selected Python tool and display its output.
    """
    tools_directory = os.path.join(os.getcwd(), 'pygame_py_files')
    tool_file = f"{tool_name}.py"
    tool_path = os.path.join(tools_directory, tool_file)
    
    if not os.path.exists(tool_path):
        flash('Tool not found.', 'danger')
        return redirect(url_for('main.tools'))
    
    try:
        # Execute the Python script using the current Python interpreter
        result = subprocess.run([sys.executable, tool_path], capture_output=True, text=True, timeout=30)
        output = result.stdout
        error = result.stderr
    except subprocess.TimeoutExpired:
        flash('The tool took too long to execute and was terminated.', 'danger')
        return redirect(url_for('main.tools'))
    except Exception as e:
        flash(f'An error occurred while running the tool: {e}', 'danger')
        logging.error(f"Error running tool {tool_name}: {e}")
        return redirect(url_for('main.tools'))
    
    if result.returncode != 0:
        flash(f'Error running tool:\n{error}', 'danger')
    else:
        flash('Tool ran successfully!', 'success')
    
    return render_template('run_tool.html', tool_name=tool_name, output=output, error=error)

@main_bp.route('/tools/upload', methods=['GET', 'POST'])
@login_required
def upload_tool():
    """
    Route to handle uploading of new Python tools.
    """
    form = UploadToolForm()
    if form.validate_on_submit():
        file = form.tool_file.data
        filename = secure_filename(file.filename)
        
        if not filename.endswith('.py'):
            flash('Only .py files are allowed.', 'warning')
            return redirect(url_for('main.upload_tool'))
        
        tools_directory = os.path.join(os.getcwd(), 'pygame_py_files')
        if not os.path.exists(tools_directory):
            os.makedirs(tools_directory)
        
        file_path = os.path.join(tools_directory, filename)
        file.save(file_path)
        
        flash('Tool uploaded successfully!', 'success')
        return redirect(url_for('main.tools'))
    
    return render_template('upload_tool.html', form=form)

