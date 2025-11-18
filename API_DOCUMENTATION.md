# API Documentation

## Base URL
```
http://localhost:5000/api/v1
```

## Authentication
API uses session-based authentication. Login via `/api/v1/auth/login` to establish a session.

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Success message",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error message",
  "errors": { ... }
}
```

### Paginated Response
```json
{
  "success": true,
  "message": "Success message",
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

## Endpoints

### Authentication

#### POST `/api/v1/auth/login`
Login and establish session.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "登入成功",
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

#### POST `/api/v1/auth/logout`
Logout and clear session.

#### GET `/api/v1/auth/me`
Get current authenticated user.

### Dashboard

#### GET `/api/v1/dashboard/stats`
Get dashboard statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_users": 10,
    "total_products": 50,
    "total_orders": 100,
    "pending_orders": 5,
    "active_products": 45
  }
}
```

#### GET `/api/v1/dashboard/recent-orders`
Get recent orders.

**Query Params:**
- `limit` (optional, default: 10): Number of orders to return

### Users

#### GET `/api/v1/users`
Get users list.

**Query Params:**
- `page` (optional, default: 1)
- `per_page` (optional, default: 20)

#### GET `/api/v1/users/<id>`
Get user by ID.

#### POST `/api/v1/users`
Create new user.

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "role": "customer"
}
```

#### PUT `/api/v1/users/<id>`
Update user.

**Request Body:**
```json
{
  "username": "updateduser",
  "email": "updated@example.com",
  "role": "admin",
  "password": "newpassword" // optional
}
```

#### DELETE `/api/v1/users/<id>`
Delete user.

### Products

#### GET `/api/v1/products`
Get products list.

**Query Params:**
- `page` (optional, default: 1)
- `per_page` (optional, default: 20)
- `category_id` (optional): Filter by category
- `search` (optional): Search in product name
- `is_active` (optional): Filter by active status

#### GET `/api/v1/products/<id>`
Get product by ID.

#### POST `/api/v1/products`
Create new product.

**Request Body (multipart/form-data):**
- `name`: Product name
- `description`: Product description
- `price`: Product price
- `stock`: Product stock
- `category_id`: Category ID
- `is_active`: Active status (optional)
- `images`: Image files (optional, multiple)

#### PUT `/api/v1/products/<id>`
Update product.

**Request Body (multipart/form-data):**
- Same as POST, plus:
- `remove_images`: List of image paths to remove

#### DELETE `/api/v1/products/<id>`
Delete product.

### Categories

#### GET `/api/v1/categories`
Get categories list.

**Query Params:**
- `parent_id` (optional): Filter by parent category
- `is_active` (optional): Filter by active status

#### GET `/api/v1/categories/<id>`
Get category by ID.

#### POST `/api/v1/categories`
Create new category.

**Request Body (multipart/form-data):**
- `name`: Category name
- `parent_id`: Parent category ID (optional)
- `description`: Category description
- `sort_order`: Sort order
- `is_active`: Active status
- `image`: Image file (optional)

#### PUT `/api/v1/categories/<id>`
Update category.

#### DELETE `/api/v1/categories/<id>`
Delete category.

### Orders

#### GET `/api/v1/orders`
Get orders list.

**Query Params:**
- `page` (optional, default: 1)
- `per_page` (optional, default: 20)
- `status` (optional): Filter by status

#### GET `/api/v1/orders/<id>`
Get order by ID (includes order items).

#### PUT `/api/v1/orders/<id>/status`
Update order status.

**Request Body:**
```json
{
  "status": "pending|processing|shipped|delivered|cancelled"
}
```

### Banners

#### GET `/api/v1/banners`
Get banners list.

**Query Params:**
- `is_active` (optional): Filter by active status

#### GET `/api/v1/banners/<id>`
Get banner by ID.

#### POST `/api/v1/banners`
Create new banner.

**Request Body (multipart/form-data):**
- `title`: Banner title
- `link`: Banner link (optional)
- `sort_order`: Sort order
- `is_active`: Active status
- `image`: Image file

#### PUT `/api/v1/banners/<id>`
Update banner.

#### DELETE `/api/v1/banners/<id>`
Delete banner.

