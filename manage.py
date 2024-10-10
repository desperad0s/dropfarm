from flask_migrate import Migrate
from backend.app import create_app
from backend.extensions import db

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()