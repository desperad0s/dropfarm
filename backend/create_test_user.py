from app import app, db
from models.models import User

def create_test_user():
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        print("Test user created successfully.")

if __name__ == '__main__':
    create_test_user()