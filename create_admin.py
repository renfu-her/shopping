#!/usr/bin/env python3
"""
Script to create admin user
Usage: python create_admin.py
"""

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Create or update admin user"""
    app = create_app()
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print('Admin user already exists!')
            print(f'Username: {admin.username}')
            print(f'Email: {admin.email}')
            print(f'Role: {admin.role}')
            # Update password
            admin.password_hash = generate_password_hash('admin123')
            db.session.commit()
            print('Password updated to: admin123')
        else:
            # Create new admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print('Admin user created successfully!')
            print('Username: admin')
            print('Password: admin123')
            print('Email: admin@example.com')
            print('Role: admin')

if __name__ == '__main__':
    create_admin_user()

