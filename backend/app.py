from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, supports_credentials=True)
db = SQLAlchemy(app)
jwt = JWTManager(app)

from api import auth, bot, projects, user

app.register_blueprint(auth.bp)
app.register_blueprint(bot.bp)
app.register_blueprint(projects.bp)
app.register_blueprint(user.bp)

if __name__ == '__main__':
    app.run(debug=True)