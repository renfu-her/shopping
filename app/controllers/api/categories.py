"""
Categories API endpoints.
"""
from flask import request
from app.controllers.api import api_bp
from app.utils.api_auth import api_login_required
from app.utils.api_response import success_response, error_response
from app.models import Category
from app import db
from app.utils.helpers import save_uploaded_file, delete_file, slugify

@api_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    Get list of categories.
    
    Query params:
        parent_id: Filter by parent category ID
        is_active: Filter by active status
    
    Returns:
        JSON response with categories list
    """
    parent_id = request.args.get('parent_id', type=int)
    is_active = request.args.get('is_active', type=bool)
    
    query = Category.query
    
    if parent_id is not None:
        query = query.filter_by(parent_id=parent_id)
    if is_active is not None:
        query = query.filter_by(is_active=is_active)
    
    categories = query.order_by(Category.sort_order, Category.id).all()
    
    categories_data = []
    for category in categories:
        categories_data.append({
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'parent_id': category.parent_id,
            'parent_name': category.parent.name if category.parent else None,
            'description': category.description,
            'image': category.image,
            'sort_order': category.sort_order,
            'is_active': category.is_active,
            'children_count': len(category.children) if category.children else 0
        })
    
    return success_response(categories_data)

@api_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """
    Get category by ID.
    
    Args:
        category_id: Category ID
        
    Returns:
        JSON response with category data
    """
    category = Category.query.get_or_404(category_id)
    
    category_data = {
        'id': category.id,
        'name': category.name,
        'slug': category.slug,
        'parent_id': category.parent_id,
        'parent_name': category.parent.name if category.parent else None,
        'description': category.description,
        'image': category.image,
        'sort_order': category.sort_order,
        'is_active': category.is_active,
        'children': [{'id': c.id, 'name': c.name} for c in category.children]
    }
    return success_response(category_data)

@api_bp.route('/categories', methods=['POST'])
@api_login_required
def create_category():
    """
    Create new category.
    
    Request body (multipart/form-data):
        name: Category name
        parent_id: Parent category ID (optional)
        description: Category description
        sort_order: Sort order
        is_active: Active status
        image: Image file (optional)
    
    Returns:
        JSON response with created category data
    """
    try:
        name = request.form.get('name', '').strip()
        parent_id = request.form.get('parent_id') or None
        description = request.form.get('description', '').strip()
        sort_order = request.form.get('sort_order', 0, type=int)
        is_active = request.form.get('is_active', 'false').lower() == 'true'
        
        if not name:
            return error_response('分類名稱不能為空', 400)
        
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
        
        category_data = {
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'parent_id': category.parent_id
        }
        return success_response(category_data, '分類建立成功', 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'建立分類失敗: {str(e)}', 400)

@api_bp.route('/categories/<int:category_id>', methods=['PUT'])
@api_login_required
def update_category(category_id):
    """
    Update category.
    
    Args:
        category_id: Category ID
        
    Request body (multipart/form-data):
        name: Category name
        parent_id: Parent category ID
        description: Category description
        sort_order: Sort order
        is_active: Active status
        image: New image file (optional)
    
    Returns:
        JSON response with updated category data
    """
    category = Category.query.get_or_404(category_id)
    
    try:
        category.name = request.form.get('name', '').strip()
        category.slug = slugify(category.name)
        parent_id = request.form.get('parent_id') or None
        category.description = request.form.get('description', '').strip()
        category.sort_order = request.form.get('sort_order', 0, type=int)
        category.is_active = request.form.get('is_active', 'false').lower() == 'true'
        
        if not category.name:
            return error_response('分類名稱不能為空', 400)
        
        # Prevent setting itself as parent
        if parent_id and int(parent_id) == category.id:
            return error_response('不能將自己設為父分類', 400)
        
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
        
        category_data = {
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'parent_id': category.parent_id
        }
        return success_response(category_data, '分類更新成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新分類失敗: {str(e)}', 400)

@api_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@api_login_required
def delete_category(category_id):
    """
    Delete category.
    
    Args:
        category_id: Category ID
        
    Returns:
        JSON response confirming deletion
    """
    category = Category.query.get_or_404(category_id)
    
    try:
        # Check if category has products
        if category.products:
            return error_response('無法刪除包含產品的分類', 400)
        
        # Check if category has children
        if category.children:
            return error_response('無法刪除包含子分類的分類', 400)
        
        # Delete image
        if category.image:
            delete_file(category.image)
        
        db.session.delete(category)
        db.session.commit()
        return success_response(None, '分類刪除成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'刪除分類失敗: {str(e)}', 400)

