from flask import render_template, request, redirect, url_for, flash, session
from app.controllers.admin import admin_bp
from app.utils.decorators import login_required, admin_required
from app.models import User
from app import db
from app.services.auth_service import AuthService

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = AuthService.login(username, password)
        if user and user.is_admin():
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    """Admin logout"""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/users')
@admin_required
def users():
    """User management list"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('users/list.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """Create new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'customer')
        
        user, error = AuthService.register(username, email, password, role)
        if user:
            flash('User created successfully', 'success')
            return redirect(url_for('admin.users'))
        else:
            flash(error or 'Failed to create user', 'danger')
    
    return render_template('users/form.html')

@admin_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    """Edit user"""
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.role = request.form.get('role', 'customer')
        
        password = request.form.get('password')
        if password:
            from werkzeug.security import generate_password_hash
            user.password_hash = generate_password_hash(password)
        
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/users/form.html', user=user)

@admin_bp.route('/users/<int:id>/delete', methods=['POST'])
@admin_required
def delete_user(id):
    """Delete user"""
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.users'))

