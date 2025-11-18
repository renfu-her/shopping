#!/bin/bash

# Script to create admin user
# Usage: ./create_admin.sh

echo "Creating admin user..."

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed or not in PATH"
    exit 1
fi

# Run Python script to create admin user
uv run python -c "
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Check if admin user already exists
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print('Admin user already exists!')
        print(f'Username: {admin.username}')
        print(f'Email: {admin.email}')
        print(f'Role: {admin.role}')
        # Update password if needed
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
"

echo "Done!"

