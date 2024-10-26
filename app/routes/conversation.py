# app/routes/conversation.py

from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    request, jsonify, send_file, session, current_app
)
from flask_login import login_required, current_user
from app.extensions import db, celery
from app.models import Conversation, Configuration, Message
from app.forms import ConversationForm, MessageForm
from datetime import datetime
import json
from werkzeug.utils import secure_filename
import os
import logging

conversation_bp = Blueprint('conversation_bp', __name__)

@celery.task(bind=True)
def process_model_inference(self, model_name, prompt, model_options):
    """
    Celery task to process model inference asynchronously.
    """
    import subprocess

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

def construct_prompt(model_info, conversation_goal, messages):
    """
    Constructs the prompt for the model based on the role, instruct statements,
    conversation history, and goal.
    """
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
    for entry in reversed(messages):
        entry_text = f"{entry.sender.username} [{entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}]: {entry.content}\n"
        if len(history_text) + len(entry_text) < max_characters:
            history_text = entry_text + history_text
        else:
            break  # Exceeds context window

    prompt += history_text
    prompt += f"{model_info.get('nickname') or model_info.get('role') or 'Model'}: "
    return prompt

@conversation_bp.route('/conversation', methods=['GET', 'POST'])
@login_required
def conversation():
    """
    Route to handle ongoing conversations.
    GET: Display the conversation with all messages.
    POST: Handle new message submissions and model inferences.
    """
    form = MessageForm()
    if request.method == 'POST':
        if 'conversation_id' not in session:
            flash('No active conversation. Please start a new conversation.', 'warning')
            return redirect(url_for('conversation_bp.start_conversation'))
        
        conversation_id = session['conversation_id']
        conversation = Conversation.query.filter_by(id=conversation_id, owner=current_user).first()
        if not conversation:
            flash('Conversation not found.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        if form.validate_on_submit():
            user_message = form.message.data.strip()
            if user_message:
                # Create a new Message entry for the user's message
                message = Message(
                    conversation=conversation,
                    sender=current_user,
                    content=user_message,
                    timestamp=datetime.utcnow()
                )
                try:
                    db.session.add(message)
                    db.session.commit()
                    flash('Your message has been sent.', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash('An error occurred while sending your message. Please try again.', 'danger')
                    current_app.logger.error(f"Error adding message: {e}")
            else:
                flash('Cannot send an empty message.', 'warning')
        
        # Initiate model inference based on the latest message
        latest_message = Message.query.filter_by(conversation=conversation).order_by(Message.timestamp.desc()).first()
        if latest_message:
            # Fetch the latest configuration
            configuration = Configuration.query.filter_by(owner=current_user).order_by(Configuration.created_at.desc()).first()
            if not configuration:
                flash('No configuration found. Please set up your conversation.', 'warning')
                return redirect(url_for('main.setup'))
            
            try:
                model_order = json.loads(configuration.model_order)
            except json.JSONDecodeError:
                flash('Invalid model order configuration.', 'danger')
                return redirect(url_for('main.setup'))
            
            inference_count = configuration.inference_count
            messages = Message.query.filter_by(conversation=conversation).order_by(Message.timestamp.asc()).all()
            current_turn = len(messages) - 1  # Subtracting the initial message
            if current_turn >= inference_count:
                flash('Conversation has reached its maximum number of inferences.', 'info')
                return redirect(url_for('conversation_bp.end_conversation'))
            
            # Determine the current model based on model_order and turn
            current_model_key = model_order[current_turn % len(model_order)]
            if current_model_key.lower() == 'omnicall':
                # Handle OmniCall input separately
                flash('OmniCall handling is not implemented yet.', 'info')
                return redirect(url_for('conversation_bp.conversation'))
            
            # Fetch models_info from session
            models_info = session.get('models_info', {})
            model_info = models_info.get(current_model_key, {})
            model_name = model_info.get('model_name', '')
            if not model_name:
                flash(f"Model '{current_model_key}' is not configured.", 'danger')
                return redirect(url_for('main.setup'))
            
            # Construct the prompt
            prompt = construct_prompt(model_info, session.get('conversation_goal', ''), messages)
            
            # Enqueue the model inference task
            task = process_model_inference.delay(model_name, prompt, model_info.get('options', {}))
            
            # Optionally, you can implement a callback or polling to handle task results asynchronously
            # For simplicity, we'll wait for the task to complete here (not recommended for production)
            result = task.get(timeout=120)  # 2-minute timeout
            
            if result['success']:
                response = result['response']
                # Create a new Message entry for the model's response
                model_message = Message(
                    conversation=conversation,
                    sender=None,  # Assuming system messages have no sender
                    content=response,
                    timestamp=datetime.utcnow()
                )
                try:
                    db.session.add(model_message)
                    db.session.commit()
                    flash(f"Response from {model_info.get('nickname') or model_info.get('role') or model_name}.", 'success')
                except Exception as e:
                    db.session.rollback()
                    flash('An error occurred while saving the model response. Please try again.', 'danger')
                    current_app.logger.error(f"Error adding model message: {e}")
            else:
                flash(f"Error from {model_info.get('nickname') or model_info.get('role') or model_name}: {result['error']}", 'danger')
        
        return redirect(url_for('conversation_bp.conversation'))
    
    # For GET requests, display the conversation
    if 'conversation_id' not in session:
        # Render initial conversation form
        return redirect(url_for('conversation_bp.start_conversation'))
    else:
        conversation_id = session['conversation_id']
        conversation = Conversation.query.filter_by(id=conversation_id, owner=current_user).first()
        if not conversation:
            flash('Conversation not found.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        messages = Message.query.filter_by(conversation=conversation).order_by(Message.timestamp.asc()).all()
        return render_template('conversation.html', conversation=conversation, messages=messages, form=form)

@conversation_bp.route('/start_conversation', methods=['GET', 'POST'])
@login_required
def start_conversation():
    """
    Route to start a new conversation.
    Utilizes ConversationForm to collect conversation details and initial message.
    """
    form = ConversationForm()
    if form.validate_on_submit():
        title = form.title.data.strip()
        initial_message = form.initial_message.data.strip()
        
        # Create a new Conversation entry
        conversation = Conversation(
            title=title,
            owner=current_user,
            configuration_id=None  # Assign if configurations are linked
        )
        try:
            db.session.add(conversation)
            db.session.commit()
            
            # Create the initial Message
            message = Message(
                conversation=conversation,
                sender=current_user,
                content=initial_message,
                timestamp=datetime.utcnow()
            )
            db.session.add(message)
            db.session.commit()
            
            # Store conversation ID in session
            session['conversation_id'] = conversation.id
            session['conversation_goal'] = ''  # Set if there's a goal to store
            
            flash('Conversation started successfully.', 'success')
            return redirect(url_for('conversation_bp.conversation'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while starting the conversation. Please try again.', 'danger')
            current_app.logger.error(f"Error starting conversation: {e}")
    
    return render_template('start_conversation.html', form=form)

@conversation_bp.route('/end_conversation', methods=['GET', 'POST'])
@login_required
def end_conversation():
    """
    Handles the end of a conversation, allowing users to save the conversation history to a file.
    """
    if 'conversation_id' not in session:
        flash('No active conversation to end.', 'warning')
        return redirect(url_for('main.home'))
    
    conversation_id = session['conversation_id']
    conversation = Conversation.query.filter_by(id=conversation_id, owner=current_user).first()
    if not conversation:
        flash('Conversation not found.', 'danger')
        return redirect(url_for('main.home'))

    messages = Message.query.filter_by(conversation=conversation).order_by(Message.timestamp.asc()).all()
    
    if request.method == 'POST':
        # Save conversation to a file
        file_name = request.form.get('file_name', 'conversation.txt').strip()
        if not file_name:
            file_name = 'conversation.txt'
        file_name = secure_filename(file_name)
        file_path = os.path.join(current_app.root_path, 'downloads', file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            with open(file_path, 'w') as f:
                for entry in messages:
                    sender = entry.sender.username if entry.sender else 'System'
                    f.write(f"{sender} [{entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}]: {entry.content}\n")
            flash('Conversation saved successfully.', 'success')
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            flash(f"Error saving conversation: {e}", 'danger')
            current_app.logger.error(f"Error saving conversation to file: {e}")
            return render_template('end_conversation.html', conversation=conversation, messages=messages)
    else:
        return render_template('end_conversation.html', conversation=conversation, messages=messages)

@conversation_bp.route('/conversation_list')
@login_required
def conversation_list():
    """
    Route to display a list of all conversations for the current user.
    """
    conversations = Conversation.query.filter_by(owner=current_user).order_by(Conversation.updated_at.desc()).all()
    return render_template('conversation_list.html', conversations=conversations)

@conversation_bp.route('/view_conversation/<int:convo_id>', methods=['GET'])
@login_required
def view_conversation(convo_id):
    """
    Route to view a specific conversation and its messages.
    """
    conversation = Conversation.query.filter_by(id=convo_id, owner=current_user).first()
    if not conversation:
        flash('Conversation not found.', 'warning')
        return redirect(url_for('conversation_bp.conversation_list'))
    
    messages = Message.query.filter_by(conversation=conversation).order_by(Message.timestamp.asc()).all()
    form = MessageForm()
    return render_template('conversation.html', conversation=conversation, messages=messages, form=form)

@conversation_bp.route('/delete_conversation/<int:convo_id>', methods=['POST'])
@login_required
def delete_conversation(convo_id):
    """
    Route to delete a specific conversation based on convo_id.
    """
    conversation = Conversation.query.filter_by(id=convo_id, owner=current_user).first()
    if not conversation:
        flash('Conversation not found.', 'warning')
        return redirect(url_for('conversation_bp.conversation_list'))
    
    try:
        db.session.delete(conversation)
        db.session.commit()
        flash('Conversation deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the conversation. Please try again.', 'danger')
        current_app.logger.error(f"Error deleting conversation: {e}")
    
    return redirect(url_for('conversation_bp.conversation_list'))
