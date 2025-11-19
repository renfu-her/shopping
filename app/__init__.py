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
    template_folder = os.path.join(root_dir, 'app', 'views')
    
    app = Flask(__name__, static_folder=static_folder, template_folder=template_folder)
    
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
        If still not found, return a placeholder SVG image instead of 404.
        """
        import os
        from flask import Response
        
        upload_folder = app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, filename)
        
        # If file exists, serve it
        if os.path.exists(file_path):
            return send_from_directory(upload_folder, filename)
        
        # If file doesn't exist and it's an image file, try WebP fallback
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
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
            
            # Image file not found - return placeholder SVG instead of 404
            # This prevents browser from showing error page
            placeholder_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300">
                <rect width="300" height="300" fill="#f0f0f0"/>
                <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#999" font-family="Arial" font-size="14">無圖片</text>
            </svg>'''
            return Response(placeholder_svg, mimetype='image/svg+xml')
        
        # Non-image file not found - return 404
        from flask import abort
        abort(404)
    
    # Helper function to handle errors
    def handle_error(error_code, error_title, error_message, error):
        """Generic error handler"""
        from flask import render_template, request, jsonify
        
        # Check if request is for API
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False, 
                'message': error_message,
                'error_code': error_code
            }), error_code
        
        # Frontend error page
        return render_template('frontend/errors/error.html',
                             error_code=error_code,
                             error_title=error_title,
                             error_message=error_message), error_code
    
    # Register error handlers for all 4xx and 5xx errors
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request errors"""
        return handle_error(400, '請求錯誤', '抱歉，您的請求格式不正確。', error)
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        """Handle 401 Unauthorized errors"""
        return handle_error(401, '未授權', '抱歉，您需要登入才能訪問此頁面。', error)
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbidden errors"""
        return handle_error(403, '禁止訪問', '抱歉，您沒有權限訪問此頁面。', error)
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors"""
        return handle_error(404, '頁面不存在', '抱歉，您訪問的頁面不存在或已被移除。', error)
    
    @app.errorhandler(405)
    def method_not_allowed_error(error):
        """Handle 405 Method Not Allowed errors"""
        return handle_error(405, '方法不允許', '抱歉，此請求方法不允許。', error)
    
    @app.errorhandler(408)
    def request_timeout_error(error):
        """Handle 408 Request Timeout errors"""
        return handle_error(408, '請求超時', '抱歉，請求超時，請稍後再試。', error)
    
    @app.errorhandler(409)
    def conflict_error(error):
        """Handle 409 Conflict errors"""
        return handle_error(409, '衝突', '抱歉，請求與當前資源狀態衝突。', error)
    
    @app.errorhandler(410)
    def gone_error(error):
        """Handle 410 Gone errors"""
        return handle_error(410, '資源已移除', '抱歉，您訪問的資源已永久移除。', error)
    
    @app.errorhandler(413)
    def payload_too_large_error(error):
        """Handle 413 Payload Too Large errors"""
        return handle_error(413, '文件過大', '抱歉，上傳的文件大小超過限制。', error)
    
    @app.errorhandler(414)
    def uri_too_long_error(error):
        """Handle 414 URI Too Long errors"""
        return handle_error(414, 'URL 過長', '抱歉，請求的 URL 過長。', error)
    
    @app.errorhandler(415)
    def unsupported_media_type_error(error):
        """Handle 415 Unsupported Media Type errors"""
        return handle_error(415, '不支援的媒體類型', '抱歉，不支援此媒體類型。', error)
    
    @app.errorhandler(429)
    def too_many_requests_error(error):
        """Handle 429 Too Many Requests errors"""
        return handle_error(429, '請求過多', '抱歉，您的請求過於頻繁，請稍後再試。', error)
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error errors"""
        return handle_error(500, '伺服器錯誤', '抱歉，伺服器發生錯誤，我們正在處理中。請稍後再試。', error)
    
    @app.errorhandler(501)
    def not_implemented_error(error):
        """Handle 501 Not Implemented errors"""
        return handle_error(501, '功能未實現', '抱歉，此功能尚未實現。', error)
    
    @app.errorhandler(502)
    def bad_gateway_error(error):
        """Handle 502 Bad Gateway errors"""
        return handle_error(502, '網關錯誤', '抱歉，伺服器網關發生錯誤，請稍後再試。', error)
    
    @app.errorhandler(503)
    def service_unavailable_error(error):
        """Handle 503 Service Unavailable errors"""
        return handle_error(503, '服務不可用', '抱歉，服務暫時不可用，我們正在維護中。請稍後再試。', error)
    
    @app.errorhandler(504)
    def gateway_timeout_error(error):
        """Handle 504 Gateway Timeout errors"""
        return handle_error(504, '網關超時', '抱歉，伺服器網關超時，請稍後再試。', error)
    
    @app.errorhandler(505)
    def http_version_not_supported_error(error):
        """Handle 505 HTTP Version Not Supported errors"""
        return handle_error(505, 'HTTP 版本不支援', '抱歉，不支援此 HTTP 版本。', error)
    
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

