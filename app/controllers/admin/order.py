"""
Order management controller for backend admin panel.
Optimized queries to prevent N+1 problems.
"""
from flask import render_template, request, redirect, url_for, flash
from app.controllers.admin import backend_bp
from app.utils.decorators import login_required
from app.models import Order, OrderItem
from app import db
from sqlalchemy.orm import joinedload

@backend_bp.route('/orders')
@login_required
def orders():
    """
    Order management list.
    
    Optimizations:
    - Eager loads order items to prevent N+1 queries when displaying order data
    """
    # Eager load order items to prevent N+1 queries
    orders = db.session.query(Order)\
        .options(joinedload(Order.items))\
        .order_by(Order.created_at.desc())\
        .all()
    
    return render_template('orders/list.html', orders=orders)

@backend_bp.route('/orders/<int:id>')
@login_required
def order_detail(id):
    """
    Order detail page.
    
    Optimizations:
    - Eager loads order items and products to prevent N+1 queries
    """
    # Eager load order items and products to prevent N+1 queries
    order = db.session.query(Order)\
        .options(
            joinedload(Order.items).joinedload(OrderItem.product)
        )\
        .filter_by(id=id)\
        .first_or_404()
    
    return render_template('orders/detail.html', order=order)

@backend_bp.route('/orders/<int:id>/update-status', methods=['POST'])
@login_required
def update_order_status(id):
    """
    Update order status.
    
    Args:
        id: Order ID
        
    Returns:
        Redirect to order detail page with flash message
    """
    from app.services.order_service import OrderService
    from app.constants import FLASH_SUCCESS, FLASH_ERROR
    
    new_status = request.form.get('status')
    if not new_status:
        flash('請選擇訂單狀態', FLASH_ERROR)
        return redirect(url_for('backend.order_detail', id=id))
    
    success, error = OrderService.update_status(id, new_status)
    
    if success:
        flash('訂單狀態更新成功', FLASH_SUCCESS)
    else:
        flash(error or '更新訂單狀態失敗', FLASH_ERROR)
    
    return redirect(url_for('backend.order_detail', id=id))
