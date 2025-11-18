from flask import render_template, request, redirect, url_for, flash
from app.controllers.admin import admin_bp
from app.utils.decorators import login_required
from app.models import Order
from app import db

@admin_bp.route('/orders')
@login_required
def orders():
    """Order management list"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Order.query
    
    if status:
        query = query.filter_by(status=status)
    
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/orders/list.html', orders=orders, status=status)

@admin_bp.route('/orders/<int:id>')
@login_required
def order_detail(id):
    """Order detail page"""
    order = Order.query.get_or_404(id)
    return render_template('admin/orders/detail.html', order=order)

@admin_bp.route('/orders/<int:id>/update-status', methods=['POST'])
@login_required
def update_order_status(id):
    """Update order status"""
    order = Order.query.get_or_404(id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        order.status = new_status
        db.session.commit()
        flash('Order status updated successfully', 'success')
    else:
        flash('Invalid status', 'danger')
    
    return redirect(url_for('admin.order_detail', id=id))

