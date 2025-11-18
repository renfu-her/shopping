"""
Dashboard API endpoints.
"""
from flask import request
from app.controllers.api import api_bp
from app.utils.api_auth import api_login_required
from app.utils.api_response import success_response
from app.models import User, Product, Order, Category, Banner
from app import db
from sqlalchemy.orm import joinedload
from app.models import OrderItem

@api_bp.route('/dashboard/stats', methods=['GET'])
@api_login_required
def get_dashboard_stats():
    """
    Get dashboard statistics.
    
    Returns:
        JSON response with dashboard statistics
    """
    stats = {
        'total_users': User.query.count(),
        'total_products': Product.query.count(),
        'total_orders': Order.query.count(),
        'total_categories': Category.query.count(),
        'total_banners': Banner.query.count(),
        'pending_orders': Order.query.filter_by(status='pending').count(),
        'active_products': Product.query.filter_by(is_active=True).count(),
    }
    return success_response(stats)

@api_bp.route('/dashboard/recent-orders', methods=['GET'])
@api_login_required
def get_recent_orders():
    """
    Get recent orders for dashboard.
    
    Query params:
        limit: Number of orders to return (default: 10)
    
    Returns:
        JSON response with recent orders
    """
    limit = request.args.get('limit', 10, type=int)
    
    # Eager load order items and products to prevent N+1 queries
    orders = db.session.query(Order)\
        .options(
            joinedload(Order.items).joinedload(OrderItem.product)
        )\
        .order_by(Order.created_at.desc())\
        .limit(limit)\
        .all()
    
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': order.id,
            'order_number': order.order_number,
            'total_amount': float(order.total_amount),
            'status': order.status,
            'created_at': order.created_at.isoformat(),
            'shipping_name': order.shipping_name
        })
    
    return success_response(orders_data)

