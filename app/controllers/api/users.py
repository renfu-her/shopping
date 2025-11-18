"""
Users API endpoints.
"""
from flask import request
from app.controllers.api import api_bp
from app.utils.api_auth import api_login_required, api_admin_required, get_current_user
from app.utils.api_response import success_response, error_response, paginated_response
from app.models import User
from app import db
from app.services.auth_service import AuthService

@api_bp.route('/users', methods=['GET'])
@api_admin_required
def get_users():
    """
    Get list of users.
    
    Query params:
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
    
    Returns:
        JSON response with paginated users list
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    users_data = []
    for user in pagination.items:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at.isoformat()
        })
    
    return paginated_response(
        users_data, page, per_page, pagination.total, '使用者列表'
    )

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@api_admin_required
def get_user(user_id):
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        JSON response with user data
    """
    user = User.query.get_or_404(user_id)
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat()
    }
    return success_response(user_data)

@api_bp.route('/users', methods=['POST'])
@api_admin_required
def create_user():
    """
    Create new user.
    
    Request body:
        {
            "username": "string",
            "email": "string",
            "password": "string",
            "role": "string" (optional, default: "customer")
        }
    
    Returns:
        JSON response with created user data
    """
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'customer')
    
    if not username or not email or not password:
        return error_response('請填寫所有必填欄位', 400)
    
    user, error = AuthService.register(username, email, password, role)
    if user:
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
        return success_response(user_data, '使用者建立成功', 201)
    else:
        return error_response(error or '建立使用者失敗', 400)

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
@api_admin_required
def update_user(user_id):
    """
    Update user.
    
    Args:
        user_id: User ID
        
    Request body:
        {
            "username": "string",
            "email": "string",
            "password": "string" (optional),
            "role": "string"
        }
    
    Returns:
        JSON response with updated user data
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    
    try:
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        role = data.get('role', user.role)
        password = data.get('password', '').strip()
        
        if not username or not email:
            return error_response('使用者名稱和電子郵件不能為空', 400)
        
        user.username = username
        user.email = email
        user.role = role
        
        if password:
            from werkzeug.security import generate_password_hash
            user.password_hash = generate_password_hash(password)
        
        db.session.commit()
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
        return success_response(user_data, '使用者更新成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新使用者失敗: {str(e)}', 400)

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
@api_admin_required
def delete_user(user_id):
    """
    Delete user.
    
    Args:
        user_id: User ID
        
    Returns:
        JSON response confirming deletion
    """
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting current user
    current_user = get_current_user()
    if current_user and current_user.id == user.id:
        return error_response('無法刪除當前登入的使用者', 400)
    
    try:
        db.session.delete(user)
        db.session.commit()
        return success_response(None, '使用者刪除成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'刪除使用者失敗: {str(e)}', 400)

