# 🌱 Dropfarm: Automated Airdrop Farming System

## 📌 Overview

Dropfarm is a scalable, headless automation system for web interactions, designed to farm airdrop tokens from new crypto projects. It interacts with Telegram chat bots and web applications to streamline the airdrop participation process.

## 🚀 Features

- 🤖 Headless automation for web interactions
- 💬 Integration with Telegram chat bots
- 🔗 Support for multiple airdrop projects (GOATS, 1Win, PX)
- 📊 User-friendly dashboard for monitoring and control
- 📈 Real-time data visualization of earnings
- 🔧 Scalable architecture using Flask, Celery, and Redis

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Backend   | Flask, Celery, SQLAlchemy |
| Frontend  | Next.js, shadcn/ui |
| Database  | PostgreSQL |
| Message Broker | Redis |
| Automation | Selenium WebDriver |

## 📁 Project Structure

dropfarm2_full-app/
├── backend/
│ ├── api/
│ ├── bot/
│ ├── celery_tasks/
│ ├── config/
│ ├── models/
│ └── tests/
├── frontend/
│ ├── components/
│ ├── pages/
│ ├── styles/
│ └── utils/
├── docker/
└── scripts/

## 🚀 Setup and Installation

### Prerequisites

- Python 3.7+
- Node.js 14+
- PostgreSQL
- Redis

### Backend Setup

1. Navigate to the backend directory and create a virtual environment:
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install dependencies and set up the database:
   ```
   pip install -r requirements.txt
   flask db upgrade
   ```

3. Configure environment variables in `.env`

### Frontend Setup

1. Install dependencies:
   ```
   cd frontend
   npm install
   ```

2. Configure environment in `.env.local`

## 🏃‍♂️ Running the Application

1. Start the backend:
   ```
   flask run
   celery -A app.celery worker --loglevel=info
   ```

2. Launch the frontend:
   ```
   npm run dev
   ```

## 🧪 Testing

| Component | Command |
|-----------|---------|
| Backend   | `pytest` |
| Frontend  | `npm test` |

## 📘 Documentation

For detailed information on deployment, contributing, and licensing, please refer to:

- 📄 [DEPLOYMENT.md](./DEPLOYMENT.md)
- 👥 [CONTRIBUTING.md](./CONTRIBUTING.md)
- ⚖️ [LICENSE.md](./LICENSE.md)

## 🙏 Acknowledgments

Special thanks to all contributors and the open-source community for their invaluable tools and libraries.

## 📬 Contact

For questions or support, please [open an issue](https://github.com/desperad0s/dropfarm/issues) on our GitHub repository.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.