"""
Frontend Blueprint initialization.
Includes context processor for global template variables.
"""
from flask import Blueprint
from app.utils.api_service import APIService

frontend_bp = Blueprint('frontend', __name__, template_folder='../../views/frontend')

@frontend_bp.context_processor
def inject_categories():
    """
    Context processor to inject categories into all templates.
    This avoids duplicate API calls across different pages.
    """
    categories_response = APIService.get_categories(
        parent_id=None,
        is_active=True
    )
    categories_data = categories_response.get('data', []) if categories_response.get('success') else []
    return dict(global_categories=categories_data)

from app.controllers.frontend import home, product, cart, contact
