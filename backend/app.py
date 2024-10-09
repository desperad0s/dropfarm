from flask import Flask
from flask_cors import CORS
from backend.celery_worker import celery  # Updated import
from .config import Config
from .routes import bot_routes
from .auth import auth_bp
from .extensions import db
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object('backend.config.Config')

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)  # Add this line

    # Setup CORS
    CORS(app, resources={r"/api/*": {"origins": Config.FRONTEND_URL}})

    # Register blueprints
    app.register_blueprint(bot_routes, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Configure Celery
    celery.conf.update(app.config)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)