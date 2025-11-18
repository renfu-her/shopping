from flask import render_template
from app.controllers.admin import admin_bp
from app.utils.decorators import login_required
from app.models import User, Product, Order, Category, Banner

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard with statistics"""
    stats = {
        'total_users': User.query.count(),
        'total_products': Product.query.count(),
        'total_orders': Order.query.count(),
        'total_categories': Category.query.count(),
        'total_banners': Banner.query.count(),
        'pending_orders': Order.query.filter_by(status='pending').count(),
        'active_products': Product.query.filter_by(is_active=True).count(),
    }
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    return render_template('dashboard.html', stats=stats, recent_orders=recent_orders)

