from flask import Flask
from flask_cors import CORS
from .celery_worker import celery
from .config import Config
from .routes import bot_routes
from .auth import auth_bp
from .extensions import db, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Setup CORS
    CORS(app, resources={r"/api/*": {"origins": Config.FRONTEND_URL}})

    # Register blueprints
    app.register_blueprint(bot_routes, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Configure Celery
    celery.conf.update(app.config)

    return app

# Remove the following lines:
# app = create_app()
# if __name__ == '__main__':
#     app.run(debug=True)