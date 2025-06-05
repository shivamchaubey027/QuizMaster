# Quiz Management System

A comprehensive web-based quiz management system built with Flask. Features include user authentication, admin dashboard, quiz creation, real-time quiz taking, and detailed analytics.

## Features

- **User Authentication**: Secure login/registration system
- **Admin Dashboard**: Complete quiz and user management
- **Quiz Builder**: Interactive quiz creation with multiple question types
- **Real-time Quiz Taking**: Timer-based quizzes with auto-save
- **Analytics**: Detailed performance tracking and history
- **Mobile Responsive**: Works seamlessly on all devices
- **Modern UI**: Clean, professional interface with animations


## The system includes:
- Beautiful landing page with gradient design
- Intuitive quiz builder for admins
- Real-time quiz interface with progress tracking
- Comprehensive results display with answer review
- User history and analytics dashboard

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Local Setup Instructions

### 1. Clone or Download the Project

If you have the project files, place them in a directory called `quiz-system`.

### 2. Create Virtual Environment

```bash
# Navigate to project directory
cd quiz-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables (Optional)

Create a `.env` file in the project root:

```bash
# .env file
SESSION_SECRET=your-secret-key-here
DATABASE_URL=sqlite:///quiz_system.db
FLASK_ENV=development
FLASK_DEBUG=True
```

### 5. Initialize Database

The database will be automatically created when you first run the application.

### 6. Run the Application

```bash
python run_local.py
```


### 7. Access the Application

Open your web browser and navigate to:
- **Application**: http://localhost:5000
- **Admin Login**: Username: `admin`, Password: `admin123`


## Default Accounts

### Admin Account
- **Username**: admin
- **Password**: admin123
- **Access**: Full admin privileges

### Creating User Accounts
Users can register themselves through the registration page, or admins can manage users through the admin dashboard.

## Usage Guide

### For Administrators

1. **Login** with admin credentials
2. **Create Quizzes**:
   - Navigate to "Create Quiz"
   - Add quiz details (title, description, time limit)
   - Add questions with multiple choice, true/false, or short answer types
   - Mark correct answers using radio buttons
   - Save the quiz
3. **Manage Users**: View user statistics and manage accounts
4. **View Results**: Export and analyze quiz results

### For Students/Users

1. **Register** a new account or login
2. **Take Quizzes**:
   - Browse available quizzes
   - Start a quiz attempt
   - Answer questions with real-time auto-save
   - Submit when complete
3. **View Results**: Review answers and performance
4. **Track Progress**: View history and statistics

## Key Features Explained

### Quiz Creation
- Support for multiple question types
- Flexible scoring system
- Time limits and attempt restrictions
- Real-time preview

### Quiz Taking
- Responsive timer with warnings
- Auto-save functionality
- Question navigation
- Progress tracking

### Results & Analytics
- Detailed answer review
- Performance statistics
- Historical tracking
- Export capabilities

## Database Schema

The system uses SQLAlchemy with the following main models:
- **User**: User accounts and authentication
- **Quiz**: Quiz metadata and settings
- **Question**: Individual questions with types and scoring
- **AnswerOption**: Multiple choice options with correct answers
- **QuizAttempt**: User quiz sessions and scores
- **UserAnswer**: Individual question responses

## Security Features

- Password hashing using Werkzeug
- CSRF protection
- Session management
- Admin role-based access control
- Input validation and sanitization

## Customization

### Styling
Modify `static/css/style.css` to customize the appearance.

### Database
Change the `DATABASE_URL` in the environment or `app.py` to use PostgreSQL or MySQL.

### Features
Add new question types by extending the models and templates.

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Use a different port
   python app.py --port=5001
   ```

2. **Database errors**:
   ```bash
   # Delete the database file and restart
   rm quiz_system.db
   python app.py
   ```

3. **Permission errors**:
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

4. **Missing dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Production Deployment

For production deployment:

1. Set proper environment variables
2. Use a production database (PostgreSQL recommended)
3. Configure a proper web server (nginx + gunicorn)
4. Enable HTTPS
5. Set secure session keys

## Support

The application includes comprehensive error handling and logging. Check the console output for debugging information.

## License

This project is open source and available under the MIT License.
