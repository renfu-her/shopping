"""
Banner management controller for backend admin panel.
Includes error handling and validation.
"""
from flask import render_template, request, redirect, url_for, flash
from app.controllers.admin import backend_bp
from app.utils.decorators import login_required
from app.models import Banner
from app import db
from app.utils.helpers import save_uploaded_file, delete_file

@backend_bp.route('/banners')
@login_required
def banners():
    """
    Banner management list.
    
    Returns:
        Rendered template with all banners
    """
    banners = Banner.query.order_by(Banner.sort_order).all()
    return render_template('banners/list.html', banners=banners)

@backend_bp.route('/banners/create', methods=['GET', 'POST'])
@login_required
def create_banner():
    """
    Create new banner.
    
    Returns:
        GET: Banner creation form
        POST: Creates banner and redirects to banner list
    """
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip() or None
            title = request.form.get('title', '').strip()
            subtitle = request.form.get('subtitle', '').strip() or None
            link = request.form.get('link', '').strip() or None
            sort_order = request.form.get('sort_order', 0, type=int)
            is_active = request.form.get('is_active') == 'on'
            
            # Validation
            if not title:
                flash('標題不能為空', 'danger')
                return render_template('banners/form.html', banner=None)
            
            banner = Banner(
                name=name,
                title=title,
                subtitle=subtitle,
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
                        flash('圖片上傳失敗', 'danger')
                        return render_template('banners/form.html', banner=None)
            
            db.session.add(banner)
            db.session.commit()
            flash('Banner 建立成功', 'success')
            return redirect(url_for('backend.banners'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'建立 Banner 失敗: {str(e)}', 'danger')
            return render_template('banners/form.html', banner=None)
    
    return render_template('banners/form.html', banner=None)

@backend_bp.route('/banners/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_banner(id):
    """
    Edit banner.
    
    Args:
        id: Banner ID
        
    Returns:
        GET: Banner edit form
        POST: Updates banner and redirects to banner list
    """
    banner = Banner.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            banner.name = request.form.get('name', '').strip() or None
            banner.title = request.form.get('title', '').strip()
            banner.subtitle = request.form.get('subtitle', '').strip() or None
            banner.link = request.form.get('link', '').strip() or None
            banner.sort_order = request.form.get('sort_order', 0, type=int)
            banner.is_active = request.form.get('is_active') == 'on'
            
            # Validation
            if not banner.title:
                flash('標題不能為空', 'danger')
                return render_template('banners/form.html', banner=banner)
            
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
            flash('Banner 更新成功', 'success')
            return redirect(url_for('backend.banners'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'更新 Banner 失敗: {str(e)}', 'danger')
            return render_template('banners/form.html', banner=banner)
    
    return render_template('banners/form.html', banner=banner)

@backend_bp.route('/banners/<int:id>/delete', methods=['POST'])
@login_required
def delete_banner(id):
    """
    Delete banner.
    
    Args:
        id: Banner ID
        
    Returns:
        Redirects to banner list with flash message
    """
    banner = Banner.query.get_or_404(id)
    
    try:
        # Delete image
        if banner.image:
            delete_file(banner.image)
        
        db.session.delete(banner)
        db.session.commit()
        flash('Banner 刪除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除 Banner 失敗: {str(e)}', 'danger')
    
    return redirect(url_for('backend.banners'))
