"""
Authentication API endpoints.
"""
from flask import request, session
from app.controllers.api import api_bp
from app.utils.api_response import success_response, error_response
from app.services.auth_service import AuthService
from app.models import User

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """
    API endpoint for user login.
    
    Request body:
        {
            "username": "string",
            "password": "string"
        }
    
    Returns:
        JSON response with user data and session info
    """
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return error_response('使用者名稱和密碼不能為空', 400)
    
    user = AuthService.login(username, password)
    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
        return success_response(user_data, '登入成功')
    else:
        return error_response('使用者名稱或密碼錯誤', 401)

@api_bp.route('/auth/logout', methods=['POST'])
def logout():
    """
    API endpoint for user logout.
    
    Returns:
        JSON response confirming logout
    """
    session.clear()
    return success_response(None, '登出成功')

@api_bp.route('/auth/me', methods=['GET'])
def get_current_user():
    """
    API endpoint to get current authenticated user.
    
    Returns:
        JSON response with current user data
    """
    if 'user_id' not in session:
        return error_response('未登入', 401)
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return error_response('使用者不存在', 401)
    
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    }
    return success_response(user_data)

