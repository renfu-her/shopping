"""
Frontend homepage controller.
Uses API service layer exclusively (all data from API).
"""
from flask import render_template
from app.controllers.frontend import frontend_bp
from app.utils.api_service import APIService

@frontend_bp.route('/')
def index():
    """
    Homepage.
    
    Uses API service layer to fetch all data (banners, products).
    Categories are provided via context processor.
    """
    # Fetch data using API service
    banners_response = APIService.get_banners(is_active=True)
    products_response = APIService.get_products(
        page=1,
        per_page=8,
        is_active=True,
        sort='newest'
    )
    
    # Extract data from responses
    banners_data = banners_response.get('data', []) if banners_response.get('success') else []
    featured_products_data = products_response.get('data', []) if products_response.get('success') else []
    
    # Categories are available via context processor as 'global_categories'
    # Pass API data directly to template (no database queries)
    return render_template('home/index.html', 
                         banners=banners_data, 
                         featured_products=featured_products_data)
