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
    
    # SEO: robots.txt
    @app.route('/robots.txt')
    def robots_txt():
        """Generate robots.txt file"""
        from flask import Response, request
        robots_content = f"""User-agent: *
Allow: /
Disallow: /backend/
Disallow: /api/
Sitemap: {request.url_root.rstrip('/')}/sitemap.xml
"""
        return Response(robots_content, mimetype='text/plain')
    
    # SEO: sitemap.xml
    @app.route('/sitemap.xml')
    def sitemap_xml():
        """Generate sitemap.xml file"""
        from flask import Response, url_for, request
        from datetime import datetime
        from app.utils.api_service import APIService
        
        with app.app_context():
            # Get all active products
            products_response = APIService.get_products(is_active=True, per_page=1000)
            products = products_response.get('data', []) if products_response.get('success') else []
            
            # Get all active categories
            categories_response = APIService.get_categories(is_active=True)
            categories = categories_response.get('data', []) if categories_response.get('success') else []
            
            sitemap = ['<?xml version="1.0" encoding="UTF-8"?>']
            sitemap.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
            
            # Homepage
            sitemap.append('  <url>')
            sitemap.append(f'    <loc>{url_for("frontend.index", _external=True)}</loc>')
            sitemap.append(f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>')
            sitemap.append('    <changefreq>daily</changefreq>')
            sitemap.append('    <priority>1.0</priority>')
            sitemap.append('  </url>')
            
            # Product list page
            sitemap.append('  <url>')
            sitemap.append(f'    <loc>{url_for("frontend.product_list", _external=True)}</loc>')
            sitemap.append(f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>')
            sitemap.append('    <changefreq>daily</changefreq>')
            sitemap.append('    <priority>0.8</priority>')
            sitemap.append('  </url>')
            
            # Category pages
            for category in categories:
                sitemap.append('  <url>')
                sitemap.append(f'    <loc>{url_for("frontend.product_list", category_id=category.get("id"), _external=True)}</loc>')
                sitemap.append(f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>')
                sitemap.append('    <changefreq>weekly</changefreq>')
                sitemap.append('    <priority>0.7</priority>')
                sitemap.append('  </url>')
            
            # Product detail pages
            for product in products:
                sitemap.append('  <url>')
                if product.get('slug'):
                    sitemap.append(f'    <loc>{url_for("frontend.product_detail", id=product.get("id"), slug=product.get("slug"), _external=True)}</loc>')
                else:
                    sitemap.append(f'    <loc>{url_for("frontend.product_detail", id=product.get("id"), _external=True)}</loc>')
                sitemap.append(f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>')
                sitemap.append('    <changefreq>weekly</changefreq>')
                sitemap.append('    <priority>0.6</priority>')
                sitemap.append('  </url>')
            
            sitemap.append('</urlset>')
            
            return Response('\n'.join(sitemap), mimetype='application/xml')
    
    return app

