#!/usr/bin/env python3
"""
Local development server runner for Quiz Management System
"""

import os
import sys

def setup_environment():
    """Set up environment variables for local development"""
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', 'True')
    os.environ.setdefault('SESSION_SECRET', 'dev-secret-key-change-in-production')
    os.environ.setdefault('DATABASE_URL', 'sqlite:///quiz_system.db')

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'flask_login', 'flask_sqlalchemy', 
        'flask_wtf', 'wtforms', 'werkzeug', 'email_validator'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall them with: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main function to run the application"""
    print("🚀 Starting Quiz Management System...")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Import and run the Flask app
    try:
        from app import app
        
        print("Dependencies loaded successfully")
        print("Database initialized")
        print("Default admin user created (if not exists)")
        print("\nDefault Login Credentials:")
        print("Username: admin")
        print("Password: admin123")
        print("\nApplication will be available at:")
        print("   http://localhost:5000")
        print("   http://127.0.0.1:5000")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        # Initialize database
        from app import init_db
        init_db()
        
        # Run the application
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()