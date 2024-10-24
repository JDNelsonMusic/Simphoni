# manage.py

import os
import sys
from flask.cli import FlaskGroup
from app import create_app, db
from flask_migrate import Migrate

# Initialize the Flask application using the factory pattern
app = create_app()

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Create a FlaskGroup instance to enable Flask CLI commands
cli = FlaskGroup(create_app=create_app)

@cli.command("create_db")
def create_db():
    """
    Creates all database tables.
    Usage: flask create_db
    """
    try:
        db.create_all()
        print("✅ Database tables created successfully.")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        sys.exit(1)

@cli.command("drop_db")
def drop_db():
    """
    Drops all database tables.
    Usage: flask drop_db
    """
    try:
        db.drop_all()
        print("✅ Database tables dropped successfully.")
    except Exception as e:
        print(f"❌ Error dropping database tables: {e}")
        sys.exit(1)

@cli.command("seed_db")
def seed_db():
    """
    Seeds the database with initial data.
    Usage: flask seed_db
    """
    try:
        from app.models import User
        from werkzeug.security import generate_password_hash

        if User.query.first():
            print("ℹ️  Database already seeded.")
            return

        user = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('password')
        )
        db.session.add(user)
        db.session.commit()
        print("✅ Database seeded with initial data.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error seeding the database: {e}")
        sys.exit(1)

@cli.command("run_app")
def run_app():
    """
    Runs the Flask development server.
    Usage: flask run_app
    """
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"❌ Error running the Flask app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    app.run(debug=True)  # Ensure debug mode is enabled