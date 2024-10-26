# app/tasks.py

from app.celery_app import make_celery
from app import create_app, db
from app.models import User  # Import your models as needed
import subprocess
import logging

# Initialize Flask application context for Celery
flask_app = create_app()
celery = make_celery(flask_app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery.task(bind=True, name='app.tasks.process_model_inference')
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

    logger.info(f"Starting model inference: {' '.join(cmd)}")

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=120)  # 2-minute timeout

        if process.returncode != 0:
            logger.error(f"Model inference failed: {stderr.strip()}")
            return {'success': False, 'error': stderr.strip()}
        else:
            logger.info(f"Model inference succeeded: {stdout.strip()}")
            return {'success': True, 'response': stdout.strip()}
    except subprocess.TimeoutExpired:
        process.kill()
        logger.error("Model inference timed out.")
        return {'success': False, 'error': 'Model inference timed out.'}
    except Exception as e:
        logger.exception("Exception during model inference.")
        return {'success': False, 'error': str(e)}
