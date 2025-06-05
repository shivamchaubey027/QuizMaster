import os
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('SESSION_SECRET', 'prod-secret-key')  # update in prod!
os.environ.setdefault('DATABASE_URL', 'sqlite:///quiz_system.db')

from app import app as application
app = app