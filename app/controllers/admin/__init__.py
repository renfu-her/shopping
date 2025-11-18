from flask import Blueprint

backend_bp = Blueprint('backend', __name__, template_folder='../../views/admin')

from app.controllers.admin import dashboard, user, category, product, order, banner

