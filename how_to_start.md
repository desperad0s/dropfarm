# How to Start the Dropfarm Application

This guide provides step-by-step instructions to set up and run both the backend and frontend of the Dropfarm application.

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm (usually comes with Node.js)
- Redis (for Celery)

## Backend Setup

1. Open a terminal and navigate to the project root directory.

2. Create a Python virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required Python packages:
   ```
   pip install -r backend/requirements.txt
   ```

5. Ensure your `.env` file in the root directory contains all necessary environment variables (refer to the existing `.env` file).

6. Start the Flask development server:
   ```
   python run.py
   ```

7. In a new terminal window (with the virtual environment activated), start the Celery worker. You have several options:

   a. Standard Celery worker:
   ```
   celery -A backend.celery_worker worker --loglevel=info
   ```

   b. Celery worker with solo pool (useful for debugging or on Windows):
   ```
   celery -A backend.celery_worker worker --loglevel=info --pool=solo
   ```

   c. Celery worker with concurrency limit:
   ```
   celery -A backend.celery_worker worker --loglevel=info --concurrency=2
   ```

   d. Celery worker with solo pool and concurrency of 1 (most restrictive, best for debugging):
   ```
   celery -A backend.celery_worker worker --loglevel=info --pool=solo --concurrency=1
   ```

   Choose the option that best suits your development environment and debugging needs.

## Frontend Setup

1. Open a new terminal and navigate to the `frontend` directory:
   ```
   cd frontend
   ```

2. Install the required npm packages:
   ```
   npm install
   ```

3. Ensure your `frontend/.env.local` file contains the necessary environment variables.

4. Start the Next.js development server:
   ```
   npm run dev
   ```

## Accessing the Application

1. Open your web browser and go to `http://localhost:3000`

2. You should see the login page. If you haven't created an account yet, use the register option to create one.

3. After logging in, you'll be redirected to the dashboard where you can test the application's features.

## Testing the Recording Functionality

1. On the dashboard, click "Add New Routine" in the Routines section.
2. Enter a name for the routine and the tokens per run.
3. Click "Start Recording".
4. A new browser window should open. Log in to Telegram if necessary.
5. Press 7 to start recording your actions.
6. Perform the actions you want to record in the Telegram web interface.
7. Press 8 to stop recording.

After recording, you should see the new routine in your list of routines on the dashboard.

## Testing the Playback Functionality

1. On the dashboard, find the routine you want to play back in the Routines section.
2. Click the "Playback" button next to the routine.
3. A new browser window should open with Telegram Web.
4. Switch to the new browser window.
5. Press 9 to start the playback.
6. The routine will now play back automatically.

## Troubleshooting

- If you encounter any issues, check the console outputs of both the frontend and backend servers for error messages.
- Ensure all required services (Redis, PostgreSQL if used) are running.
- Verify that all environment variables are correctly set in both `.env` and `frontend/.env.local` files.
- If Celery tasks are not executing, try using the solo pool option when starting the Celery worker.
- For Windows users, the solo pool is often necessary due to limitations with process forking.

## Debugging Celery

- To debug Celery tasks, use the `--pool=solo` option when starting the worker. This runs tasks synchronously in the main process.
- Increase the log level for more detailed output: `--loglevel=debug`
- To run Celery in the foreground for easier debugging, add the `--foreground` flag to the Celery command.

If you continue to experience problems, please refer to the project documentation or seek assistance from the development team.