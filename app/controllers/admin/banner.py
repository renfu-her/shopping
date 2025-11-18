from flask import render_template, request, redirect, url_for, flash
from app.controllers.admin import admin_bp
from app.utils.decorators import login_required
from app.models import Banner
from app import db
from app.utils.helpers import save_uploaded_file, delete_file

@admin_bp.route('/banners')
@login_required
def banners():
    """Banner management list"""
    banners = Banner.query.order_by(Banner.sort_order).all()
    return render_template('admin/banners/list.html', banners=banners)

@admin_bp.route('/banners/create', methods=['GET', 'POST'])
@login_required
def create_banner():
    """Create new banner"""
    if request.method == 'POST':
        title = request.form.get('title')
        link = request.form.get('link') or None
        sort_order = request.form.get('sort_order', 0, type=int)
        is_active = request.form.get('is_active') == 'on'
        
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
                    flash('Failed to upload image', 'danger')
                    return render_template('admin/banners/form.html', banner=None)
        
        db.session.add(banner)
        db.session.commit()
        flash('Banner created successfully', 'success')
        return redirect(url_for('admin.banners'))
    
    return render_template('admin/banners/form.html', banner=None)

@admin_bp.route('/banners/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_banner(id):
    """Edit banner"""
    banner = Banner.query.get_or_404(id)
    
    if request.method == 'POST':
        banner.title = request.form.get('title')
        banner.link = request.form.get('link') or None
        banner.sort_order = request.form.get('sort_order', 0, type=int)
        banner.is_active = request.form.get('is_active') == 'on'
        
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
        flash('Banner updated successfully', 'success')
        return redirect(url_for('admin.banners'))
    
    return render_template('admin/banners/form.html', banner=banner)

@admin_bp.route('/banners/<int:id>/delete', methods=['POST'])
@login_required
def delete_banner(id):
    """Delete banner"""
    banner = Banner.query.get_or_404(id)
    
    # Delete image
    if banner.image:
        delete_file(banner.image)
    
    db.session.delete(banner)
    db.session.commit()
    flash('Banner deleted successfully', 'success')
    return redirect(url_for('admin.banners'))

