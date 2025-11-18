"""
Products API endpoints.
"""
from flask import request
from app.controllers.api import api_bp
from app.utils.api_auth import api_login_required
from app.utils.api_response import success_response, error_response, paginated_response
from app.models import Product, Category
from app import db
from app.utils.helpers import save_uploaded_file, delete_file, slugify
from sqlalchemy.orm import joinedload
from typing import List

@api_bp.route('/products', methods=['GET'])
def get_products():
    """
    Get list of products.
    
    Query params:
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
        category_id: Filter by category ID
        search: Search in product name
        is_active: Filter by active status
    
    Returns:
        JSON response with paginated products list
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '').strip()
    is_active = request.args.get('is_active', type=bool)
    
    query = db.session.query(Product).options(joinedload(Product.category))
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search:
        query = query.filter(Product.name.contains(search))
    if is_active is not None:
        query = query.filter_by(is_active=is_active)
    
    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    products_data = []
    for product in pagination.items:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'description': product.description,
            'price': float(product.price),
            'stock': product.stock,
            'category_id': product.category_id,
            'category_name': product.category.name if product.category else None,
            'images': product.get_images(),
            'is_active': product.is_active,
            'created_at': product.created_at.isoformat()
        })
    
    return paginated_response(
        products_data, page, per_page, pagination.total, '產品列表'
    )

@api_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    Get product by ID.
    
    Args:
        product_id: Product ID
        
    Returns:
        JSON response with product data
    """
    product = db.session.query(Product)\
        .options(joinedload(Product.category))\
        .get_or_404(product_id)
    
    product_data = {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'description': product.description,
        'price': float(product.price),
        'stock': product.stock,
        'category_id': product.category_id,
        'category_name': product.category.name if product.category else None,
        'images': product.get_images(),
        'is_active': product.is_active,
        'created_at': product.created_at.isoformat(),
        'updated_at': product.updated_at.isoformat()
    }
    return success_response(product_data)

@api_bp.route('/products', methods=['POST'])
@api_login_required
def create_product():
    """
    Create new product.
    
    Request body (multipart/form-data):
        name: Product name
        description: Product description
        price: Product price
        stock: Product stock
        category_id: Category ID
        is_active: Active status (optional)
        images: Image files (optional, multiple)
    
    Returns:
        JSON response with created product data
    """
    try:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', type=float)
        stock = request.form.get('stock', type=int)
        category_id = request.form.get('category_id', type=int)
        is_active = request.form.get('is_active', 'false').lower() == 'true'
        
        if not name:
            return error_response('產品名稱不能為空', 400)
        if price is None or price < 0:
            return error_response('價格必須大於等於0', 400)
        if stock is None or stock < 0:
            return error_response('庫存必須大於等於0', 400)
        
        product = Product(
            name=name,
            slug=slugify(name),
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
            is_active=is_active
        )
        
        # Handle image uploads
        images = []
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename:
                    image_path = save_uploaded_file(file, 'products')
                    if image_path:
                        images.append(image_path)
        
        product.set_images(images)
        
        db.session.add(product)
        db.session.commit()
        
        product_data = {
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'price': float(product.price),
            'stock': product.stock,
            'images': product.get_images()
        }
        return success_response(product_data, '產品建立成功', 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'建立產品失敗: {str(e)}', 400)

@api_bp.route('/products/<int:product_id>', methods=['PUT'])
@api_login_required
def update_product(product_id):
    """
    Update product.
    
    Args:
        product_id: Product ID
        
    Request body (multipart/form-data):
        name: Product name
        description: Product description
        price: Product price
        stock: Product stock
        category_id: Category ID
        is_active: Active status
        images: New image files (optional)
        remove_images: List of image paths to remove (optional)
    
    Returns:
        JSON response with updated product data
    """
    product = Product.query.get_or_404(product_id)
    
    try:
        product.name = request.form.get('name', '').strip()
        product.slug = slugify(product.name)
        product.description = request.form.get('description', '').strip()
        product.price = request.form.get('price', type=float)
        product.stock = request.form.get('stock', type=int)
        product.category_id = request.form.get('category_id', type=int)
        product.is_active = request.form.get('is_active', 'false').lower() == 'true'
        
        if not product.name:
            return error_response('產品名稱不能為空', 400)
        
        # Handle image uploads
        images = product.get_images()
        
        # Add new images
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename:
                    image_path = save_uploaded_file(file, 'products')
                    if image_path:
                        images.append(image_path)
        
        # Remove images
        remove_images = request.form.getlist('remove_images')
        for img in remove_images:
            if img in images:
                delete_file(img)
                images.remove(img)
        
        product.set_images(images)
        
        db.session.commit()
        
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'stock': product.stock,
            'images': product.get_images()
        }
        return success_response(product_data, '產品更新成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新產品失敗: {str(e)}', 400)

@api_bp.route('/products/<int:product_id>', methods=['DELETE'])
@api_login_required
def delete_product(product_id):
    """
    Delete product.
    
    Args:
        product_id: Product ID
        
    Returns:
        JSON response confirming deletion
    """
    product = Product.query.get_or_404(product_id)
    
    try:
        # Delete images
        for img in product.get_images():
            delete_file(img)
        
        db.session.delete(product)
        db.session.commit()
        return success_response(None, '產品刪除成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'刪除產品失敗: {str(e)}', 400)

