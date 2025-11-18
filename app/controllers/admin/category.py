"""
Category management controller for backend admin panel.
Optimized queries and error handling.
"""
from flask import render_template, request, redirect, url_for, flash
from app.controllers.admin import backend_bp
from app.utils.decorators import login_required
from app.models import Category
from app import db
from app.utils.helpers import save_uploaded_file, delete_file, slugify
from typing import Optional

@backend_bp.route('/categories')
@login_required
def categories():
    """
    Category management list.
    
    Returns:
        Rendered template with all categories
    """
    categories = Category.query.order_by(Category.sort_order, Category.id).all()
    return render_template('categories/list.html', categories=categories)

@backend_bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    """
    Create new category.
    
    Returns:
        GET: Category creation form
        POST: Creates category and redirects to category list
    """
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            parent_id = request.form.get('parent_id') or None
            description = request.form.get('description', '').strip()
            sort_order = request.form.get('sort_order', 0, type=int)
            is_active = request.form.get('is_active') == 'on'
            
            # Validation
            if not name:
                flash('分類名稱不能為空', 'danger')
                all_categories = Category.query.all()
                return render_template('categories/form.html', category=None, all_categories=all_categories)
            
            # Validate parent_id if provided
            if parent_id:
                parent = Category.query.get(parent_id)
                if not parent:
                    flash('父分類不存在', 'danger')
                    all_categories = Category.query.all()
                    return render_template('categories/form.html', category=None, all_categories=all_categories)
            
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
            flash('分類建立成功', 'success')
            return redirect(url_for('backend.categories'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'建立分類失敗: {str(e)}', 'danger')
            all_categories = Category.query.all()
            return render_template('categories/form.html', category=None, all_categories=all_categories)
    
    # Get all categories for parent selection
    all_categories = Category.query.all()
    return render_template('categories/form.html', category=None, all_categories=all_categories)

@backend_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    """
    Edit category.
    
    Args:
        id: Category ID
        
    Returns:
        GET: Category edit form
        POST: Updates category and redirects to category list
    """
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            category.name = request.form.get('name', '').strip()
            category.slug = slugify(category.name)
            parent_id = request.form.get('parent_id') or None
            category.description = request.form.get('description', '').strip()
            category.sort_order = request.form.get('sort_order', 0, type=int)
            category.is_active = request.form.get('is_active') == 'on'
            
            # Validation
            if not category.name:
                flash('分類名稱不能為空', 'danger')
                all_categories = Category.query.filter(Category.id != id).all()
                return render_template('categories/form.html', category=category, all_categories=all_categories)
            
            # Prevent setting itself as parent
            if parent_id and int(parent_id) == category.id:
                flash('不能將自己設為父分類', 'danger')
                all_categories = Category.query.filter(Category.id != id).all()
                return render_template('categories/form.html', category=category, all_categories=all_categories)
            
            # Validate parent_id if provided
            if parent_id:
                parent = Category.query.get(parent_id)
                if not parent:
                    flash('父分類不存在', 'danger')
                    all_categories = Category.query.filter(Category.id != id).all()
                    return render_template('categories/form.html', category=category, all_categories=all_categories)
            
            category.parent_id = parent_id
            
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
            flash('分類更新成功', 'success')
            return redirect(url_for('backend.categories'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'更新分類失敗: {str(e)}', 'danger')
            all_categories = Category.query.filter(Category.id != id).all()
            return render_template('categories/form.html', category=category, all_categories=all_categories)
    
    # Get all categories for parent selection (exclude current and its children)
    all_categories = Category.query.filter(Category.id != id).all()
    return render_template('categories/form.html', category=category, all_categories=all_categories)

@backend_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    """
    Delete category.
    
    Args:
        id: Category ID
        
    Returns:
        Redirects to category list with flash message
    """
    category = Category.query.get_or_404(id)
    
    try:
        # Check if category has products
        if category.products:
            flash('無法刪除包含產品的分類', 'danger')
            return redirect(url_for('backend.categories'))
        
        # Check if category has children
        if category.children:
            flash('無法刪除包含子分類的分類', 'danger')
            return redirect(url_for('backend.categories'))
        
        # Delete image
        if category.image:
            delete_file(category.image)
        
        db.session.delete(category)
        db.session.commit()
        flash('分類刪除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除分類失敗: {str(e)}', 'danger')
    
    return redirect(url_for('backend.categories'))
