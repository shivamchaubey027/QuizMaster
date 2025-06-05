#!/usr/bin/env python3
"""
Quiz System Setup Script
Automatically sets up the quiz management system
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_requirements():
    """Install required packages"""
    requirements = [
        "Flask==2.3.3",
        "Flask-SQLAlchemy==3.0.5",
        "Flask-Login==0.6.3",
        "Flask-WTF==1.1.1",
        "WTForms==3.0.1",
        "Werkzeug==2.3.7"
    ]
    
    for package in requirements:
        if not run_command(f"pip install {package}", f"Installing {package.split('==')[0]}"):
            return False
    return True

def create_database():
    """Create and initialize the database"""
    print("🔄 Setting up database...")
    
    # Set environment variables
    os.environ['DATABASE_URL'] = 'sqlite:///quiz_system.db'
    os.environ['SESSION_SECRET'] = 'development-secret-key-please-change-in-production'
    
    try:
        # Import and initialize the app
        from app import app, db
        from models import User, Quiz, Question, AnswerOption, QuizAttempt, UserAnswer
        
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Check if admin user exists
            admin_user = User.query.filter_by(is_admin=True).first()
            if not admin_user:
                from werkzeug.security import generate_password_hash
                admin = User(
                    username='admin',
                    email='admin@quiz.com',
                    password_hash=generate_password_hash('admin123'),
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Default admin user created: admin/admin123")
            else:
                print("✅ Admin user already exists")
        
        print("✅ Database setup completed")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_sample_quiz():
    """Create a sample quiz for testing"""
    print("🔄 Creating sample quiz...")
    
    try:
        from app import app, db
        from models import User, Quiz, Question, AnswerOption
        
        with app.app_context():
            # Check if sample quiz already exists
            sample_quiz = Quiz.query.filter_by(title='Sample Quiz').first()
            if sample_quiz:
                print("✅ Sample quiz already exists")
                return True
            
            admin_user = User.query.filter_by(is_admin=True).first()
            if not admin_user:
                print("❌ No admin user found")
                return False
            
            # Create sample quiz
            quiz = Quiz(
                title='Sample Quiz',
                description='A sample quiz to test the system',
                created_by=admin_user.id,
                time_limit=10,
                max_attempts=3,
                is_active=True
            )
            db.session.add(quiz)
            db.session.flush()
            
            # Add sample questions
            questions_data = [
                {
                    'text': 'What is the capital of France?',
                    'type': 'multiple_choice',
                    'options': [
                        ('Paris', True),
                        ('London', False),
                        ('Berlin', False),
                        ('Madrid', False)
                    ]
                },
                {
                    'text': 'Python is a programming language.',
                    'type': 'true_false',
                    'options': [
                        ('True', True),
                        ('False', False)
                    ]
                },
                {
                    'text': 'What does HTML stand for?',
                    'type': 'short_answer',
                    'options': []
                }
            ]
            
            for i, q_data in enumerate(questions_data):
                question = Question(
                    quiz_id=quiz.id,
                    question_text=q_data['text'],
                    question_type=q_data['type'],
                    points=1,
                    order_index=i
                )
                db.session.add(question)
                db.session.flush()
                
                for option_text, is_correct in q_data['options']:
                    option = AnswerOption(
                        question_id=question.id,
                        option_text=option_text,
                        is_correct=is_correct
                    )
                    db.session.add(option)
            
            db.session.commit()
            print("✅ Sample quiz created successfully")
            return True
            
    except Exception as e:
        print(f"❌ Sample quiz creation failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Starting Quiz System Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    print("\n📦 Installing Dependencies")
    if not install_requirements():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create database
    print("\n🗄️ Setting up Database")
    if not create_database():
        print("❌ Failed to setup database")
        sys.exit(1)
    
    # Create sample quiz
    print("\n📝 Creating Sample Content")
    create_sample_quiz()  # This is optional, so we don't exit on failure
    
    # Setup complete
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Run the application: python main.py")
    print("2. Open your browser to: http://localhost:5000")
    print("3. Login as admin: admin/admin123")
    print("4. Create your first quiz!")
    print("\n🔐 Security Note:")
    print("Please change the default admin password in production!")
    
if __name__ == "__main__":
    main()
