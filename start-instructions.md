# Start Instructions for Dropfarm Application

Follow these steps to start the Dropfarm application environment:

1. Activate the virtual environment (from the project root):
   ```
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

2. Start the Flask backend (in one terminal):
   ```
   python run.py
   ```

3. Start the Celery worker (in a new terminal, after activating the virtual environment):
   ```
   celery -A backend.celery_config:celery_app worker --loglevel=info --pool=solo
   ```

4. Start the frontend (in another new terminal):
   ```
   cd frontend
   npm run dev
   ```

Important Notes:
- Run these commands in separate terminal windows or tabs.
- Keep all processes running simultaneously.
- Ensure your Redis server is running (it's used as the message broker for Celery).
- Run all commands from the project root directory, except for the frontend command which should be run from the `frontend` directory.
- If you encounter permission issues, try running your command prompt or PowerShell as an administrator.

To stop the application:
- Use Ctrl+C in each terminal to stop the respective processes.
- Deactivate the virtual environment when you're done:
  ```
  deactivate
  ```

Remember to check your `.env` files for any necessary environment variables before starting the application.