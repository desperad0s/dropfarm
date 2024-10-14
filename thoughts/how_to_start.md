# How to Start the Dropfarm Application

## Prerequisites
- Python 3.8+
- Node.js 14+
- PostgreSQL
- Redis

## Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: ``
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up the database:
   ```
   flask db upgrade
   ```

6. Start the Flask server:
   ```
   flask run
   ```

7. In a new terminal, start the Celery worker:
   ```
   celery -A backend.celery_worker worker --loglevel=info --pool=solo
   ```

## Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

## Calibration Process

1. Open the application in your browser.
2. Navigate to the Calibration page.
3. Follow the on-screen instructions to perform the calibration:
   - Click on the 5 calibration points as accurately as possible.
   - Take your time to ensure precise clicks.
4. After calibration, test the accuracy using the provided tools.
5. If the calibration is not satisfactory, repeat the process.

## Recording and Playback

1. Use the recording feature to capture your actions.
2. Review and edit recorded actions as needed.
3. Use the playback feature to automate tasks.

## Troubleshooting

- If you encounter offset issues during calibration or playback, try the following:
  - Ensure your screen resolution matches the application settings.
  - Perform calibration at a slower pace, focusing on accuracy.
  - If issues persist, consider adjusting the transformation algorithm in `backend/calibration.py`.

For more detailed information, refer to the documentation in the `docs` folder.
