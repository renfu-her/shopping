"""
WSGI entry point for the shopping platform application.
Can be used with production servers like Gunicorn, uWSGI, etc.
Also can be run directly: 
    python wsgi.py
    or
    uv run wsgi.py
"""
from app import create_app, db
from app.database import init_db
import os

# Create the Flask application instance
application = create_app()

# Initialize database when running directly
if __name__ == '__main__':
    with application.app_context():
        db.create_all()
        init_db()
    
    # Run the application directly when executed
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    application.run(host='0.0.0.0', port=port, debug=debug)

