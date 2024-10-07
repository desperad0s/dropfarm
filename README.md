# 🌱 Dropfarm

Dropfarm is a scalable, headless automation system for web interactions, specifically designed for farming airdrop tokens from new crypto projects.

## ✨ Features

- Headless browser automation using Selenium
- Record and playback functionality for creating custom routines
- User authentication and session management
- Dashboard for monitoring bot status and activities
- Support for multiple routines (GOATS, 1Win, PX)
- Dark mode support

## 🛠️ Tech Stack

- Backend:
  - Flask
  - Celery
  - Redis
  - SQLAlchemy

- Frontend:
  - Next.js
  - React
  - TypeScript

- Database:
  - SQLite (can be easily switched to PostgreSQL for production)

- UI Components:
  - shadcn/ui

## 🚀 Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/dropfarm.git
   cd dropfarm
   ```

2. Set up the backend:
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```
   cd frontend
   npm install
   ```

4. Start the Redis server:
   ```
   redis-server
   ```

5. Start the Celery worker:
   ```
   celery -A backend.celery_app:celery_app worker --loglevel=info
   ```

6. Start the Flask backend:
   ```
   python backend/app.py
   ```

7. Start the Next.js frontend:
   ```
   npm run dev
   ```

8. Open your browser and navigate to `http://localhost:3000`

## 📘 Usage

1. Register a new account or log in to an existing one.

2. Navigate to the dashboard to see the bot status and controls.

3. Use the "Record New Routine" feature to create custom routines.

4. Start and stop routines as needed.

5. Monitor bot activities and earnings on the dashboard.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgements

Special thanks to all contributors and the open-source community for making this project possible.

## 📞 Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.

Happy farming!