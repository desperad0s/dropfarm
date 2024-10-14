# Dropfarm Development Cheat Sheet

## Virtual Environment

1. Create a venv:
   ```
   python -m venv venv
   ```

2. Activate venv:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Deactivate venv:
   ```
   deactivate
   ```

## Dependencies

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Update requirements.txt:
   ```
   pip freeze > requirements.txt
   ```

## Database

1. Initialize database:
   ```
   flask db init
   ```

2. Create a migration:
   ```
   flask db migrate -m "Description of changes"
   ```

3. Apply migrations:
   ```
   flask db upgrade
   ```

## Running the Application

1. Set environment variables:
   ```
   export FLASK_APP=manage.py
   export FLASK_ENV=development
   ```

2. Run Flask app:
   ```
   flask run
   ```

3. Run Celery worker:
   ```
   celery -A manage.celery worker --loglevel=info
   ```

## Common Issues

- Always activate your venv before working on the project
- Make sure your database is running before starting the Flask app
- Check that your .env file has all necessary environment variables
- If you get a "Module not found" error, make sure you're in the correct directory and your venv is activated

## Git Workflow

1. Check status: `git status`
2. Add changes: `git add .`
3. Commit changes: `git commit -m "Descriptive message"`
4. Push changes: `git push origin main`

Remember: Always pull before starting work and push your changes regularly!

## Database Management

1. Database location:
   - The database file (dropfarm.db) should be in the `backend` directory.
   - The `migrations` folder should also be in the `backend` directory.

2. Resetting the database:
   ```
   cd backend
   rm -rf instance migrations *.db
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

3. After making changes to models:
   ```
   flask db migrate -m "Description of changes"
   flask db upgrade
   ```

4. Checking database content (for SQLite):
   ```
   sqlite3 dropfarm.db
   .tables
   SELECT * FROM table_name;
   .quit
   ```

Remember: Always backup your database before making significant changes!

## PostgreSQL Setup

1. Install PostgreSQL:
   - Windows: Download and install from postgresql.org
   - macOS: `brew install postgresql`
   - Ubuntu: `sudo apt-get install postgresql`

2. Start PostgreSQL service:
   - Windows: It should start automatically
   - macOS: `brew services start postgresql`
   - Ubuntu: `sudo service postgresql start`

3. Create a new database:
   ```
   psql -U postgres
   CREATE DATABASE dropfarm;
   \q
   ```

4. Update `backend/config.py` with your PostgreSQL credentials:
   ```python
   SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/dropfarm'
   ```

5. Initialize the database (from backend directory):
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

Remember to replace 'user' and 'password' with your actual PostgreSQL credentials!

## Troubleshooting Flask and Database Issues

1. Import errors with 'backend':
   If you encounter import errors related to 'backend', ensure that your Python path includes the parent directory of the 'backend' folder. You can add this to your PYTHONPATH environment variable or use absolute imports in your Python files.

   Example of absolute imports:
   ```python
   from backend.config import Config
   from backend.extensions import db
   ```

2. Flask db init issues:
   If `flask db init` fails, try the following:

   a. Ensure you're in the correct directory (usually the 'backend' folder).

   b. Set the FLASK_APP environment variable:
      - Windows: `set FLASK_APP=manage.py`
      - macOS/Linux: `export FLASK_APP=manage.py`

   c. Use Python to run Flask commands:
      ```
      python -m flask db init
      ```

   d. If using `manage.py`, try:
      ```
      python manage.py db init
      ```

3. Database connection issues:
   - Ensure your PostgreSQL service is running.
   - Check that the database URL in your config or .env file is correct:
     ```
     DATABASE_URL=postgresql://username:password@localhost:5432/dropfarm
     ```
   - Verify that the 'dropfarm' database exists in PostgreSQL.

4. After resolving import or database issues:
   Always run migrations to ensure your database schema is up to date:
   ```
   flask db migrate -m "Your migration message"
   flask db upgrade
   ```

Remember: Always activate your virtual environment before running Flask or database commands!

## Command Prompt (cmd) vs PowerShell

When working with Python projects on Windows, you may encounter differences between Command Prompt (cmd) and PowerShell. Here are some key points to remember:

1. Command execution:
   - In cmd, use: `command1 & command2`
   - In PowerShell, use: `command1; command2`

2. Environment variables:
   - In cmd, set: `set VARIABLE_NAME=value`
   - In PowerShell, set: `$env:VARIABLE_NAME = "value"`

3. Deleting files and directories:
   - In cmd:
     ```
     rmdir /s /q folder_name
     del file_name
     ```
   - In PowerShell:
     ```
     Remove-Item -Recurse -Force folder_name
     Remove-Item file_name
     ```

4. Activating virtual environment:
   - In cmd: `venv\Scripts\activate`
   - In PowerShell: `.\venv\Scripts\Activate.ps1`

5. Running Python:
   - Both cmd and PowerShell: `python script.py`

6. Flask commands:
   - Both cmd and PowerShell: `flask command_name`
   - If issues arise, try: `python -m flask command_name`

Remember: For consistency in Python projects, it's often easier to use Command Prompt (cmd) as it aligns more closely with Unix-like terminals used in many development environments.

Tip: If you need to use PowerShell, you can make it behave more like cmd for certain operations by starting it with the `-NoProfile` flag:
```
powershell.exe -NoProfile
```
This can help avoid some PowerShell-specific issues when running scripts designed for cmd.