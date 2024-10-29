# app/utils.py

import json
from .models import CustomModel
from flask import current_app

def prepare_configuration_context(user, configuration=None):
    """
    Prepares context variables for setup and edit_configuration views.
    
    :param user: The current user object.
    :param configuration: (Optional) The configuration object being edited.
    :return: Dictionary containing models_info, model_order, available_models, and custom_models.
    """
    # Define available models (same as in setup view)
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

    # Fetch custom models uploaded by the user
    custom_models = CustomModel.query.filter_by(owner=user).all()

    # Determine model_order
    if configuration:
        try:
            model_order = json.loads(configuration.model_order)
        except json.JSONDecodeError:
            current_app.logger.error(f"Invalid JSON in configuration.id={configuration.id}: {configuration.model_order}")
            model_order = []
    else:
        # Default model_order if no configuration is provided
        model_order = [f'slot_{i}' for i in range(1, 10)]

    # Fetch models_info from configuration or initialize
    if configuration:
        try:
            models_info = json.loads(configuration.model_order)
        except json.JSONDecodeError:
            current_app.logger.error(f"Invalid JSON in configuration.id={configuration.id}: {configuration.model_order}")
            models_info = {}
    else:
        models_info = {}

    # Alternatively, if models_info is more complex, adjust accordingly
    # For this example, we'll assume it's a dict with slot IDs as keys

    return {
        'models_info': models_info,
        'model_order': model_order,
        'available_models': available_models,
        'custom_models': custom_models
    }
