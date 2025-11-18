from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User
from app import db

class AuthService:
    @staticmethod
    def login(username, password):
        """Authenticate user and return user object if successful"""
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            return user
        return None
    
    @staticmethod
    def register(username, email, password, role='customer'):
        """Register new user"""
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return None, "Username already exists"
        if User.query.filter_by(email=email).first():
            return None, "Email already exists"
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()
        return user, None
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Change user password"""
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        if not check_password_hash(user.password_hash, old_password):
            return False, "Current password is incorrect"
        
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return True, None

