from flask import render_template
from app.controllers.frontend import frontend_bp
from app.models import Banner, Product, Category

@frontend_bp.route('/')
def index():
    """Homepage"""
    # Get active banners
    banners = Banner.query.filter_by(is_active=True).order_by(Banner.sort_order).all()
    
    # Get featured products (active products, limit 8)
    featured_products = Product.query.filter_by(is_active=True).limit(8).all()
    
    # Get categories for navigation
    categories = Category.query.filter_by(is_active=True, parent_id=None).all()
    
    return render_template('frontend/home/index.html', 
                         banners=banners, 
                         featured_products=featured_products,
                         categories=categories)

