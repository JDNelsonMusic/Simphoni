# app/routes/conversation.py

from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    request, jsonify, send_file, session
)
from flask_login import login_required, current_user
from app.extensions import db
from app.celery_app import celery
from app.models import Conversation, Configuration
from datetime import datetime
import json
from werkzeug.utils import secure_filename
import os
import logging
import subprocess

conversation_bp = Blueprint('conversation_bp', __name__)

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
                user_id=current_user.id
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
                user_id=current_user.id
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
