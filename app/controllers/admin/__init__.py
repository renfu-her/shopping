from flask import Blueprint

admin_bp = Blueprint('admin', __name__, template_folder='../../views/admin')

from app.controllers.admin import dashboard, user, category, product, order, banner

