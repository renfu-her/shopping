# Shopping Platform

E-commerce shopping platform built with Flask, SQLAlchemy, and MySQL.

## Features

### Frontend
- Homepage with banners and featured products
- Product listing with categories and search
- Product detail pages
- Shopping cart
- Contact page

### Backend Admin
- Dashboard with statistics
- User management
- Hierarchical category management
- Product management with image upload
- Order management
- Banner management

## Setup

1. Install dependencies using uv:
```bash
uv sync
```

2. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

3. Update `.env` with your MySQL database credentials

4. Initialize database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. Run the application:
```bash
# Option 1: Using wsgi.py (recommended for production)
python wsgi.py

# Option 2: Using run.py (development)
python run.py
```

For production deployment with Gunicorn:
```bash
gunicorn wsgi:application
```

## Default Admin Credentials

- Username: `admin`
- Password: `admin123`

**Important**: Change the default admin password in production!

## Project Structure

- `app/` - Main application code
  - `models/` - Database models
  - `controllers/` - Route handlers
  - `views/` - Jinja2 templates
  - `services/` - Business logic
  - `utils/` - Utility functions
- `public/` - Static files
- `uploads/` - Uploaded images

