# Local Setup Instructions for Quiz Management System

## Quick Start Guide

### Step 1: Prerequisites
- Python 3.8 or higher
- Git (optional)
- Code editor (VS Code recommended)

### Step 2: Download/Clone Project
Place all project files in a folder called `quiz-system`

### Step 3: Open in VS Code
```bash
cd quiz-system
code .
```

### Step 4: Create Virtual Environment
Open VS Code terminal (Ctrl+` or View > Terminal) and run:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 6: Run the Application
```bash
python app.py
```

**Alternative method:**
```bash
python run_local.py
```

### Step 7: Access Application
Open browser and go to: http://localhost:5000

## Default Login Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

## Project Structure
```
quiz-system/
├── app.py              # Main application
├── models.py           # Database models
├── auth.py             # Authentication
├── admin.py            # Admin panel
├── quiz.py             # Quiz functionality
├── config.py           # Configuration
├── utils.py            # Helper functions
├── requirements.txt    # Dependencies
├── run_local.py        # Local runner script
├── static/             # CSS, JS, images
├── templates/          # HTML templates
└── instance/           # Database files
```

## Troubleshooting

### Common Issues:

1. **"No module named 'flask'"**
   - Solution: Activate virtual environment and install requirements

2. **"Address already in use"**
   - Solution: Change port in app.py or kill existing process

3. **Database errors**
   - Solution: Delete `quiz_system.db` file and restart

4. **Permission denied**
   - Solution: Run as administrator or check file permissions

### VS Code Setup Tips:

1. **Python Interpreter**: Select the virtual environment interpreter
   - Ctrl+Shift+P → "Python: Select Interpreter"
   - Choose `./venv/Scripts/python.exe` (Windows) or `./venv/bin/python` (Mac/Linux)

2. **Extensions**: Install these helpful extensions:
   - Python
   - Flask Snippets
   - Jinja (for templates)

3. **Run Configuration**: Create `.vscode/launch.json`:
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Flask App",
               "type": "python",
               "request": "launch",
               "program": "${workspaceFolder}/app.py",
               "console": "integratedTerminal",
               "env": {
                   "FLASK_ENV": "development",
                   "FLASK_DEBUG": "1"
               }
           }
       ]
   }
   ```

## Features Overview

### Admin Features:
- Create and manage quizzes
- Add multiple question types (multiple choice, true/false, short answer)
- Mark correct answers
- Set time limits and attempt restrictions
- View user statistics and results
- Export quiz results

### User Features:
- Register and login
- Take quizzes with real-time timer
- Auto-save answers
- View detailed results
- Track performance history
- Mobile-responsive interface

### Technical Features:
- SQLite database (easily changeable to PostgreSQL)
- Session management
- CSRF protection
- Password hashing
- Responsive design
- Modern UI with animations

## Environment Variables (Optional)

Create `.env` file for custom configuration:
```
SESSION_SECRET=your-secret-key
DATABASE_URL=sqlite:///quiz_system.db
FLASK_ENV=development
FLASK_DEBUG=True
```

## Production Deployment Notes

For production deployment:
1. Set `FLASK_ENV=production`
2. Use PostgreSQL or MySQL database
3. Configure proper web server (nginx + gunicorn)
4. Set secure session secret
5. Enable HTTPS

## Support

- Check console output for error messages
- Ensure virtual environment is activated
- Verify all dependencies are installed
- Check file permissions and paths