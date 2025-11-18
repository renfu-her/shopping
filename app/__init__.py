from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='development'):
    # Get the root directory (parent of app directory)
    import os
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_folder = os.path.join(root_dir, 'static')
    
    app = Flask(__name__, static_folder=static_folder)
    
    # Load configuration
    from app.config import Config
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints (admin first to ensure template priority)
    from app.controllers.admin import admin_bp
    from app.controllers.frontend import frontend_bp
    
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(frontend_bp)
    
    # Create upload directories
    upload_folder = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder + '/products', exist_ok=True)
    os.makedirs(upload_folder + '/banners', exist_ok=True)
    os.makedirs(upload_folder + '/categories', exist_ok=True)
    
    # Serve uploaded files
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    return app

