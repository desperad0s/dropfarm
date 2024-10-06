from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from database import engine, Base
from routes import init_routes

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this!
CORS(app)
api = Api(app)
jwt = JWTManager(app)

# Initialize the database
Base.metadata.create_all(bind=engine)

# Initialize routes
init_routes(app)

if __name__ == '__main__':
    app.run(debug=True)