# app/tasks.py

from app import celery
import subprocess
import logging

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
