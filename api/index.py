import os

os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('SESSION_SECRET', os.getenv('SESSION_SECRET', 'change-this-in-vercel-env-settings!'))
os.environ.setdefault('DATABASE_URL', os.getenv('DATABASE_URL', 'sqlite:///quiz_system.db'))


from app import app
