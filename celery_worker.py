from celery import Celery
from app import create_app

app = create_app()
celery = Celery(
    app.import_name,
    broker='amqp://guest:guest@localhost:5672//',
    backend='rpc://'
)
celery.conf.update(app.config)

TaskBase = celery.Task

class ContextTask(TaskBase):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)

celery.Task = ContextTask
