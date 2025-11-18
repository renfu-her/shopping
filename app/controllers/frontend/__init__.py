from flask import Blueprint

frontend_bp = Blueprint('frontend', __name__, template_folder='../../views/frontend')

from app.controllers.frontend import home, product, cart, contact

