"""
User management controller for backend admin panel.
Uses API service layer for data operations.
"""
from flask import render_template, request, redirect, url_for, flash, session
from app.controllers.admin import backend_bp
from app.utils.decorators import login_required, admin_required
from app.utils.api_service import APIService
from app.models import User
from app.services.auth_service import AuthService

@backend_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Admin login page.
    
    Returns:
        GET: Login form
        POST: Authenticates user and redirects to dashboard
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('請輸入使用者名稱和密碼', 'danger')
            return render_template('login.html')
        
        user = AuthService.login(username, password)
        if user and user.is_admin():
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('登入成功！', 'success')
            return redirect(url_for('backend.dashboard'))
        else:
            flash('使用者名稱或密碼錯誤', 'danger')
    
    return render_template('login.html')

@backend_bp.route('/logout')
@login_required
def logout():
    """
    Admin logout.
    
    Returns:
        Redirects to login page
    """
    session.clear()
    flash('登出成功', 'info')
    return redirect(url_for('backend.login'))

@backend_bp.route('/users')
@admin_required
def users():
    """
    User management list.
    
    Uses API service to fetch users.
    """
    page = request.args.get('page', 1, type=int)
    response = APIService.get_users(page=page, per_page=1000)  # Get all for DataTables
    
    if response.get('success'):
        users_data = response.get('data', [])
        # Convert to User objects for template compatibility
        user_ids = [u['id'] for u in users_data]
        users = User.query.filter(User.id.in_(user_ids)).order_by(User.created_at.desc()).all()
        return render_template('users/list.html', users=users)
    else:
        flash('取得使用者列表失敗', 'danger')
        return render_template('users/list.html', users=[])

@backend_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """
    Create new user.
    
    Uses API service for user creation.
    """
    if request.method == 'POST':
        # Call API endpoint via HTTP or use service directly
        from flask import jsonify
        import requests
        
        data = {
            'username': request.form.get('username', '').strip(),
            'email': request.form.get('email', '').strip(),
            'password': request.form.get('password', ''),
            'role': request.form.get('role', 'customer')
        }
        
        # Make API call
        try:
            response = requests.post(
                f'http://localhost:5000/api/v1/users',
                json=data,
                cookies=request.cookies
            )
            api_response = response.json()
            
            if api_response.get('success'):
                flash('使用者建立成功', 'success')
                return redirect(url_for('backend.users'))
            else:
                flash(api_response.get('message', '建立使用者失敗'), 'danger')
        except Exception as e:
            flash(f'建立使用者失敗: {str(e)}', 'danger')
    
    return render_template('users/form.html')

@backend_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    """
    Edit user.
    
    Uses API service for user update.
    """
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        import requests
        
        data = {
            'username': request.form.get('username', '').strip(),
            'email': request.form.get('email', '').strip(),
            'role': request.form.get('role', 'customer'),
        }
        
        password = request.form.get('password', '').strip()
        if password:
            data['password'] = password
        
        try:
            response = requests.put(
                f'http://localhost:5000/api/v1/users/{id}',
                json=data,
                cookies=request.cookies
            )
            api_response = response.json()
            
            if api_response.get('success'):
                flash('使用者更新成功', 'success')
                return redirect(url_for('backend.users'))
            else:
                flash(api_response.get('message', '更新使用者失敗'), 'danger')
        except Exception as e:
            flash(f'更新使用者失敗: {str(e)}', 'danger')
    
    return render_template('users/form.html', user=user)

@backend_bp.route('/users/<int:id>/delete', methods=['POST'])
@admin_required
def delete_user(id):
    """
    Delete user.
    
    Uses API service for user deletion.
    """
    import requests
    
    try:
        response = requests.delete(
            f'http://localhost:5000/api/v1/users/{id}',
            cookies=request.cookies
        )
        api_response = response.json()
        
        if api_response.get('success'):
            flash('使用者刪除成功', 'success')
        else:
            flash(api_response.get('message', '刪除使用者失敗'), 'danger')
    except Exception as e:
        flash(f'刪除使用者失敗: {str(e)}', 'danger')
    
    return redirect(url_for('backend.users'))
