# run.py

import os
from app import create_app

# Determine the configuration to use based on the FLASK_ENV environment variable
config_name = os.getenv('FLASK_ENV', 'development')

app = create_app()

if __name__ == '__main__':
    # Run the Flask application with settings based on the environment
    if config_name == 'production':
        app.run(host='0.0.0.0', port=8000)
    else:
        app.run(host='127.0.0.1', port=5000, debug=True)
