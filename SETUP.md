# Setup Instructions

## Prerequisites
- Python 3.9+
- MySQL Server
- uv package manager

## Installation Steps

1. **Install dependencies using uv:**
```bash
uv sync
```

2. **Create `.env` file:**
Copy `.env.example` to `.env` and update with your MySQL credentials:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=shopping_db
SECRET_KEY=your-secret-key-here
```

3. **Create MySQL database:**
```sql
CREATE DATABASE shopping_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. **Initialize database:**
```bash
# Using uv
uv run flask db init
uv run flask db migrate -m "Initial migration"
uv run flask db upgrade
```

Or simply run the application once - it will create tables automatically:
```bash
uv run wsgi.py
```

5. **Run the application:**
```bash
# Using uv (recommended)
uv run wsgi.py

# Or directly
python wsgi.py
# or
python run.py
```

The application will be available at:
- Frontend: http://localhost:5000
- Backend Panel: http://localhost:5000/backend

## Default Admin Credentials
- Username: `admin`
- Password: `admin123`

**Important**: Change the default admin password in production!

## Static Files
The application expects static files (CSS, JS, images) to be in a `static/` directory. You may need to copy the static assets from the docs folder or use a CDN.

## Upload Directory
Uploaded images will be stored in the `uploads/` directory:
- `uploads/products/` - Product images
- `uploads/banners/` - Banner images
- `uploads/categories/` - Category images

Make sure these directories have write permissions.

