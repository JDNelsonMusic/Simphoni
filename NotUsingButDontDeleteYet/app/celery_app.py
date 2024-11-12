# app/celery_app.py

from celery import Celery

celery = Celery()  # Define Celery instance at the module level

def make_celery(app):
    """
    Initialize Celery with Flask app context.
    """
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND']
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
