from flask import render_template, request, redirect, url_for, flash
from app.controllers.admin import admin_bp
from app.utils.decorators import login_required
from app.models import Category
from app import db
from app.utils.helpers import save_uploaded_file, delete_file, slugify

@admin_bp.route('/categories')
@login_required
def categories():
    """Category management list"""
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('categories/list.html', categories=categories)

@admin_bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    """Create new category"""
    if request.method == 'POST':
        name = request.form.get('name')
        parent_id = request.form.get('parent_id') or None
        description = request.form.get('description')
        sort_order = request.form.get('sort_order', 0, type=int)
        is_active = request.form.get('is_active') == 'on'
        
        category = Category(
            name=name,
            slug=slugify(name),
            parent_id=parent_id if parent_id else None,
            description=description,
            sort_order=sort_order,
            is_active=is_active
        )
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                image_path = save_uploaded_file(image_file, 'categories')
                if image_path:
                    category.image = image_path
        
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully', 'success')
        return redirect(url_for('admin.categories'))
    
    # Get all categories for parent selection
    all_categories = Category.query.all()
    return render_template('categories/form.html', category=None, all_categories=all_categories)

@admin_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    """Edit category"""
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.slug = slugify(category.name)
        parent_id = request.form.get('parent_id') or None
        # Prevent setting itself as parent
        if parent_id and int(parent_id) != category.id:
            category.parent_id = parent_id
        category.description = request.form.get('description')
        category.sort_order = request.form.get('sort_order', 0, type=int)
        category.is_active = request.form.get('is_active') == 'on'
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                # Delete old image
                if category.image:
                    delete_file(category.image)
                # Save new image
                image_path = save_uploaded_file(image_file, 'categories')
                if image_path:
                    category.image = image_path
        
        db.session.commit()
        flash('Category updated successfully', 'success')
        return redirect(url_for('admin.categories'))
    
    # Get all categories for parent selection (exclude current and its children)
    all_categories = Category.query.filter(Category.id != id).all()
    return render_template('admin/categories/form.html', category=category, all_categories=all_categories)

@admin_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    """Delete category"""
    category = Category.query.get_or_404(id)
    
    # Check if category has products
    if category.products:
        flash('Cannot delete category with products', 'danger')
        return redirect(url_for('admin.categories'))
    
    # Delete image
    if category.image:
        delete_file(category.image)
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully', 'success')
    return redirect(url_for('admin.categories'))

