"""
Banners API endpoints.
"""
from flask import request
from app.controllers.api import api_bp
from app.utils.api_auth import api_login_required
from app.utils.api_response import success_response, error_response
from app.models import Banner
from app import db
from app.utils.helpers import save_uploaded_file, delete_file

@api_bp.route('/banners', methods=['GET'])
def get_banners():
    """
    Get list of banners.
    
    Query params:
        is_active: Filter by active status
    
    Returns:
        JSON response with banners list
    """
    is_active = request.args.get('is_active', type=bool)
    
    query = Banner.query
    if is_active is not None:
        query = query.filter_by(is_active=is_active)
    
    banners = query.order_by(Banner.sort_order).all()
    
    banners_data = []
    for banner in banners:
        banners_data.append({
            'id': banner.id,
            'title': banner.title,
            'link': banner.link,
            'image': banner.image,
            'sort_order': banner.sort_order,
            'is_active': banner.is_active
        })
    
    return success_response(banners_data)

@api_bp.route('/banners/<int:banner_id>', methods=['GET'])
def get_banner(banner_id):
    """
    Get banner by ID.
    
    Args:
        banner_id: Banner ID
        
    Returns:
        JSON response with banner data
    """
    banner = Banner.query.get_or_404(banner_id)
    
    banner_data = {
        'id': banner.id,
        'title': banner.title,
        'link': banner.link,
        'image': banner.image,
        'sort_order': banner.sort_order,
        'is_active': banner.is_active
    }
    return success_response(banner_data)

@api_bp.route('/banners', methods=['POST'])
@api_login_required
def create_banner():
    """
    Create new banner.
    
    Request body (multipart/form-data):
        title: Banner title
        link: Banner link (optional)
        sort_order: Sort order
        is_active: Active status
        image: Image file
    
    Returns:
        JSON response with created banner data
    """
    try:
        title = request.form.get('title', '').strip()
        link = request.form.get('link', '').strip() or None
        sort_order = request.form.get('sort_order', 0, type=int)
        is_active = request.form.get('is_active', 'false').lower() == 'true'
        
        if not title:
            return error_response('標題不能為空', 400)
        
        banner = Banner(
            title=title,
            link=link,
            sort_order=sort_order,
            is_active=is_active
        )
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                image_path = save_uploaded_file(image_file, 'banners')
                if image_path:
                    banner.image = image_path
                else:
                    return error_response('圖片上傳失敗', 400)
        
        db.session.add(banner)
        db.session.commit()
        
        banner_data = {
            'id': banner.id,
            'title': banner.title,
            'image': banner.image
        }
        return success_response(banner_data, 'Banner 建立成功', 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'建立 Banner 失敗: {str(e)}', 400)

@api_bp.route('/banners/<int:banner_id>', methods=['PUT'])
@api_login_required
def update_banner(banner_id):
    """
    Update banner.
    
    Args:
        banner_id: Banner ID
        
    Request body (multipart/form-data):
        title: Banner title
        link: Banner link
        sort_order: Sort order
        is_active: Active status
        image: New image file (optional)
    
    Returns:
        JSON response with updated banner data
    """
    banner = Banner.query.get_or_404(banner_id)
    
    try:
        banner.title = request.form.get('title', '').strip()
        banner.link = request.form.get('link', '').strip() or None
        banner.sort_order = request.form.get('sort_order', 0, type=int)
        banner.is_active = request.form.get('is_active', 'false').lower() == 'true'
        
        if not banner.title:
            return error_response('標題不能為空', 400)
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                # Delete old image
                if banner.image:
                    delete_file(banner.image)
                # Save new image
                image_path = save_uploaded_file(image_file, 'banners')
                if image_path:
                    banner.image = image_path
        
        db.session.commit()
        
        banner_data = {
            'id': banner.id,
            'title': banner.title,
            'image': banner.image
        }
        return success_response(banner_data, 'Banner 更新成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新 Banner 失敗: {str(e)}', 400)

@api_bp.route('/banners/<int:banner_id>', methods=['DELETE'])
@api_login_required
def delete_banner(banner_id):
    """
    Delete banner.
    
    Args:
        banner_id: Banner ID
        
    Returns:
        JSON response confirming deletion
    """
    banner = Banner.query.get_or_404(banner_id)
    
    try:
        # Delete image
        if banner.image:
            delete_file(banner.image)
        
        db.session.delete(banner)
        db.session.commit()
        return success_response(None, 'Banner 刪除成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'刪除 Banner 失敗: {str(e)}', 400)

