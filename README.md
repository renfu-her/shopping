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

This will create a virtual environment and install all dependencies automatically.

2. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

3. Update `.env` with your MySQL database credentials

4. Initialize database:
```bash
# Using uv
uv run flask db init
uv run flask db migrate -m "Initial migration"
uv run flask db upgrade

# Or directly
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. Run the application:
```bash
# Option 1: Using uv (recommended)
uv run wsgi.py

# Option 2: Using wsgi.py directly
python wsgi.py

# Option 3: Using run.py (development)
python run.py
```

For production deployment with Gunicorn:
```bash
# Using uv
uv run gunicorn wsgi:application

# Or directly
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

