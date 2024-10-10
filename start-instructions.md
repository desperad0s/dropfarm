# Dropfarm Application Start Instructions

This document provides instructions on how to start the Dropfarm application environment.

## Prerequisites

- Ensure you have Python 3.7+ installed
- Make sure you have Redis installed and running
- Ensure PostgreSQL is installed and running

## Setup

1. Clone the repository (if you haven't already):
   ```
   git clone <repository-url>
   cd dropfarm2_full-app
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Ensure your `.env` file is in the root directory and contains all necessary environment variables.

## Starting the Application

1. Start the Flask application:
   ```
   python run.py
   ```
   The application should now be running on `http://localhost:5000`

2. In a new terminal window, start the Celery worker:
   ```
   celery -A backend.celery_worker.celery worker --loglevel=info
   ```

## Additional Commands

- To run Flask in debug mode:
  ```
  flask run --debug
  ```

- To run database migrations:
  ```
  flask db upgrade
  ```

Remember to always activate your virtual environment before running any commands.

## Troubleshooting

If you encounter any issues:
1. Ensure all required services (Redis, PostgreSQL) are running.
2. Check that your `.env` file contains all necessary environment variables.
3. Make sure you're in the root directory of the project when running commands.
4. Verify that your virtual environment is activated.

If problems persist, please refer to the project documentation or contact the development team.