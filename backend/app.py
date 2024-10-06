from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from api.routes import api

app = Flask(__name__)
app.config.from_object('config.Config')

CORS(app)
jwt = JWTManager(app)
db.init_app(app)

app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)