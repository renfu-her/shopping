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
    
    # Register blueprints (order doesn't matter since templates use unique names)
    from app.controllers.api import api_bp
    from app.controllers.frontend import frontend_bp
    from app.controllers.admin import backend_bp
    
    # Register frontend (root path / maps to frontend)
    app.register_blueprint(frontend_bp)
    # Register backend with /backend prefix
    app.register_blueprint(backend_bp, url_prefix='/backend')
    # Register API
    app.register_blueprint(api_bp)
    
    # Create upload directories and convert to absolute path
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.isabs(upload_folder):
        # Convert relative path to absolute path
        upload_folder = os.path.join(root_dir, upload_folder)
    app.config['UPLOAD_FOLDER'] = upload_folder
    
    os.makedirs(upload_folder + '/products', exist_ok=True)
    os.makedirs(upload_folder + '/banners', exist_ok=True)
    os.makedirs(upload_folder + '/categories', exist_ok=True)
    
    # Serve uploaded files with WebP fallback
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """
        Serve uploaded files with automatic WebP fallback.
        If the requested file doesn't exist and it's an image file,
        try to serve the corresponding WebP version.
        """
        import os
        from flask import abort
        
        upload_folder = app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, filename)
        
        # If file exists, serve it
        if os.path.exists(file_path):
            return send_from_directory(upload_folder, filename)
        
        # If file doesn't exist and it's an image file, try WebP fallback
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif'}
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext in image_extensions:
            # Try to find corresponding WebP file
            webp_filename = os.path.splitext(filename)[0] + '.webp'
            webp_path = os.path.join(upload_folder, webp_filename)
            
            if os.path.exists(webp_path):
                # Set proper content type for WebP
                response = send_from_directory(upload_folder, webp_filename)
                response.headers['Content-Type'] = 'image/webp'
                return response
        
        # File not found
        abort(404)
    
    return app

