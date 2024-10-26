# app/routes/__init__.py

from .main import main_bp
from .auth import auth_bp
from .conversation import conversation_bp

# Register all blueprints
def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(conversation_bp)
