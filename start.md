# Starting the Dropfarm Application

This guide explains how to start both the backend and frontend components of the Dropfarm application.

## Backend Setup

1. Open a command prompt and navigate to the backend directory:
   ```
   cd path/to/your/project/backend
   ```

2. Activate the virtual environment:
   ```
   backend_env\Scripts\activate
   ```

3. Start the Flask application:
   ```
   python run.py
   ```

4. Open a new command prompt, navigate to the backend directory, activate the virtual environment, and start Celery:
   ```
   cd path/to/your/project/backend
   backend_env\Scripts\activate
   python start_celery.py
   ```

## Frontend Setup

1. Open a new command prompt and navigate to the frontend directory:
   ```
   cd path/to/your/project/frontend
   ```

2. Start the Next.js development server:
   ```
   npm run dev
   ```

## Accessing the Application

Once both backend and frontend are running:

1. The backend API will be available at `http://localhost:5000`
2. The frontend will be accessible at `http://localhost:3000`

Open your web browser and go to `http://localhost:3000` to use the Dropfarm application.

## Stopping the Application

To stop the application:

1. In each command prompt window, press Ctrl+C to stop the running process.
2. For the backend virtual environment, you can deactivate it by running:
   ```
   deactivate
   ```

Remember to always activate the virtual environment before running backend commands, and ensure you're in the correct directory for each component.
