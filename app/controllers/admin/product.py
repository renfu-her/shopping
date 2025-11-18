"""
Product management controller for backend admin panel.
Optimized queries to prevent N+1 problems.
"""
from flask import render_template, request, redirect, url_for, flash
from app.controllers.admin import backend_bp
from app.utils.decorators import login_required
from app.models import Product, Category
from app import db
from app.utils.helpers import save_uploaded_file, delete_file, slugify
from sqlalchemy.orm import joinedload
from typing import Optional, List

@backend_bp.route('/products')
@login_required
def products():
    """
    Product management list.
    
    Optimizations:
    - Eager loads category relationship to prevent N+1 queries
    """
    # Eager load category to prevent N+1 queries
    products = db.session.query(Product)\
        .options(joinedload(Product.category))\
        .order_by(Product.created_at.desc())\
        .all()
    
    # Categories for filter dropdown
    categories = Category.query.all()
    
    return render_template('products/list.html', products=products, categories=categories)

@backend_bp.route('/products/create', methods=['GET', 'POST'])
@login_required
def create_product():
    """
    Create new product.
    
    Returns:
        GET: Product creation form
        POST: Creates product and redirects to product list
    """
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            price = request.form.get('price', type=float)
            stock = request.form.get('stock', type=int)
            category_id = request.form.get('category_id', type=int)
            is_active = request.form.get('is_active') == 'on'
            
            # Validation
            if not name:
                flash('產品名稱不能為空', 'danger')
                categories = Category.query.all()
                return render_template('products/form.html', product=None, categories=categories)
            
            if price is None or price < 0:
                flash('價格必須大於等於0', 'danger')
                categories = Category.query.all()
                return render_template('products/form.html', product=None, categories=categories)
            
            if stock is None or stock < 0:
                flash('庫存必須大於等於0', 'danger')
                categories = Category.query.all()
                return render_template('products/form.html', product=None, categories=categories)
            
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
            images = _process_image_uploads('products')
            product.set_images(images)
            
            db.session.add(product)
            db.session.commit()
            flash('產品建立成功', 'success')
            return redirect(url_for('backend.products'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'建立產品失敗: {str(e)}', 'danger')
            categories = Category.query.all()
            return render_template('products/form.html', product=None, categories=categories)
    
    categories = Category.query.all()
    return render_template('products/form.html', product=None, categories=categories)

@backend_bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    """
    Edit product.
    
    Args:
        id: Product ID
        
    Returns:
        GET: Product edit form
        POST: Updates product and redirects to product list
    """
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            product.name = request.form.get('name', '').strip()
            product.slug = slugify(product.name)
            product.description = request.form.get('description', '').strip()
            product.price = request.form.get('price', type=float)
            product.stock = request.form.get('stock', type=int)
            product.category_id = request.form.get('category_id', type=int)
            product.is_active = request.form.get('is_active') == 'on'
            
            # Validation
            if not product.name:
                flash('產品名稱不能為空', 'danger')
                categories = Category.query.all()
                return render_template('products/form.html', product=product, categories=categories)
            
            # Handle image uploads
            images = product.get_images()
            
            # Add new images
            new_images = _process_image_uploads('products')
            images.extend(new_images)
            
            # Remove images
            remove_images = request.form.getlist('remove_images')
            for img in remove_images:
                if img in images:
                    delete_file(img)
                    images.remove(img)
            
            product.set_images(images)
            
            db.session.commit()
            flash('產品更新成功', 'success')
            return redirect(url_for('backend.products'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'更新產品失敗: {str(e)}', 'danger')
            categories = Category.query.all()
            return render_template('products/form.html', product=product, categories=categories)
    
    categories = Category.query.all()
    return render_template('products/form.html', product=product, categories=categories)

@backend_bp.route('/products/<int:id>/delete', methods=['POST'])
@login_required
def delete_product(id):
    """
    Delete product.
    
    Args:
        id: Product ID
        
    Returns:
        Redirects to product list with flash message
    """
    product = Product.query.get_or_404(id)
    
    try:
        # Delete images
        for img in product.get_images():
            delete_file(img)
        
        db.session.delete(product)
        db.session.commit()
        flash('產品刪除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除產品失敗: {str(e)}', 'danger')
    
    return redirect(url_for('backend.products'))


def _process_image_uploads(folder: str) -> List[str]:
    """
    Process uploaded image files.
    
    Args:
        folder: Upload folder name (e.g., 'products', 'banners')
        
    Returns:
        List of image paths
    """
    from flask import request
    images = []
    if 'images' in request.files:
        files = request.files.getlist('images')
        for file in files:
            if file and file.filename:
                image_path = save_uploaded_file(file, folder)
                if image_path:
                    images.append(image_path)
    return images
