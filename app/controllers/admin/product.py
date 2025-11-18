from flask import render_template, request, redirect, url_for, flash
from app.controllers.admin import admin_bp
from app.utils.decorators import login_required
from app.models import Product, Category
from app import db
from app.utils.helpers import save_uploaded_file, delete_file, slugify
import json

@admin_bp.route('/products')
@login_required
def products():
    """Product management list"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', type=int)
    
    query = Product.query
    
    if search:
        query = query.filter(Product.name.contains(search))
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    products = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    categories = Category.query.all()
    
    return render_template('admin/products/list.html', products=products, categories=categories, 
                         search=search, category_id=category_id)

@admin_bp.route('/products/create', methods=['GET', 'POST'])
@login_required
def create_product():
    """Create new product"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price', type=float)
        stock = request.form.get('stock', type=int)
        category_id = request.form.get('category_id', type=int)
        is_active = request.form.get('is_active') == 'on'
        
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
        flash('Product created successfully', 'success')
        return redirect(url_for('admin.products'))
    
    categories = Category.query.all()
    return render_template('admin/products/form.html', product=None, categories=categories)

@admin_bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    """Edit product"""
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.slug = slugify(product.name)
        product.description = request.form.get('description')
        product.price = request.form.get('price', type=float)
        product.stock = request.form.get('stock', type=int)
        product.category_id = request.form.get('category_id', type=int)
        product.is_active = request.form.get('is_active') == 'on'
        
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
        flash('Product updated successfully', 'success')
        return redirect(url_for('admin.products'))
    
    categories = Category.query.all()
    return render_template('admin/products/form.html', product=product, categories=categories)

@admin_bp.route('/products/<int:id>/delete', methods=['POST'])
@login_required
def delete_product(id):
    """Delete product"""
    product = Product.query.get_or_404(id)
    
    # Delete images
    for img in product.get_images():
        delete_file(img)
    
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully', 'success')
    return redirect(url_for('admin.products'))

