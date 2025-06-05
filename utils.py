from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minutes"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"

def calculate_percentage(score, total):
    """Calculate percentage score"""
    if total == 0:
        return 0
    return round((score / total) * 100, 1)
