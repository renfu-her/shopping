"""
Dashboard controller for backend admin panel.
Uses API service layer to fetch data.
"""
from flask import render_template
from app.controllers.admin import backend_bp
from app.utils.decorators import login_required
from app.utils.api_service import APIService

@backend_bp.route('/')
@backend_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Admin dashboard with statistics.
    
    Uses API service layer to fetch data.
    """
    # Get statistics from API service
    stats_response = APIService.get_dashboard_stats()
    stats = stats_response.get('data', {})
    
    # Get recent orders from API service
    orders_response = APIService.get_recent_orders(limit=10)
    recent_orders_data = orders_response.get('data', [])
    
    # Convert ISO format dates back to datetime objects for template
    from datetime import datetime
    from app.models import Order
    
    recent_orders = []
    for order_data in recent_orders_data:
        order = Order.query.get(order_data['id'])
        if order:
            recent_orders.append(order)
    
    return render_template('dashboard.html', stats=stats, recent_orders=recent_orders)
