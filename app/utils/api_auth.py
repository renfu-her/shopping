"""
API authentication decorators and utilities.
"""
from functools import wraps
from flask import request, session, jsonify
from app.models import User
from app.utils.api_response import error_response
from typing import Optional

def api_login_required(f):
    """
    Decorator to require login for API routes.
    Returns JSON response instead of redirect.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return error_response('Authentication required', 401)
        return f(*args, **kwargs)
    return decorated_function

def api_admin_required(f):
    """
    Decorator to require admin role for API routes.
    Returns JSON response instead of redirect.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return error_response('Authentication required', 401)
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin():
            return error_response('Admin privileges required', 403)
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user() -> Optional[User]:
    """
    Get current authenticated user from session.
    
    Returns:
        User object or None if not authenticated
    """
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None
