from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Import all API modules to register routes
from app.controllers.api import auth
from app.controllers.api import users
from app.controllers.api import products
from app.controllers.api import categories
from app.controllers.api import orders
from app.controllers.api import banners
from app.controllers.api import dashboard
from app.controllers.api import cart

