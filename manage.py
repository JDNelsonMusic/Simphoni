# manage.py

import sys
from flask.cli import FlaskGroup
from app import create_app, db
from flask_migrate import Migrate
from app.models import User
from app.celery_app import make_celery
from werkzeug.security import generate_password_hash

# Initialize the Flask application using the factory pattern
app = create_app()

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Celery
celery = make_celery(app)

# Create a FlaskGroup instance to enable Flask CLI commands
cli = FlaskGroup(create_app=create_app)

@cli.command("create_db")
def create_db():
    """Creates the database tables."""
    db.create_all()
    db.session.commit()
    print("✅ Database tables created successfully.")

@cli.command("drop_db")
def drop_db():
    """Drops the database tables."""
    db.drop_all()
    db.session.commit()
    print("✅ Database tables dropped successfully.")

@cli.command("seed_db")
def seed_db():
    """Seeds the database with initial data."""
    if User.query.first():
        print("ℹ️ Database already seeded.")
        return
    user = User(
        username='admin',
        email='admin@example.com',
        password_hash=generate_password_hash('password')
    )
    db.session.add(user)
    db.session.commit()
    print("✅ Database seeded with initial data.")

@cli.command("celery_worker")
def celery_worker():
    """Starts the Celery worker."""
    try:
        celery.worker_main(argv=['celery', 'worker', '--loglevel=info'])
    except Exception as e:
        print(f"❌ Error starting Celery worker: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli()
