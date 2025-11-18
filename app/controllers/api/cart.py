"""
Cart API endpoints for frontend.
"""
from flask import request, session
from app.controllers.api import api_bp
from app.utils.api_response import success_response, error_response
from app.models import Product
from app.services.cart_service import CartService

@api_bp.route('/cart', methods=['GET'])
def get_cart():
    """
    Get shopping cart items.
    
    Returns:
        JSON response with cart items and total
    """
    cart_items = CartService.get_cart_items()
    total = CartService.calculate_total(cart_items)
    
    cart_data = {
        'items': cart_items,
        'total': float(total),
        'item_count': len(cart_items)
    }
    
    return success_response(cart_data)

@api_bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    """
    Add product to cart.
    
    Request body:
        {
            "product_id": int,
            "quantity": int (default: 1)
        }
    
    Returns:
        JSON response confirming addition
    """
    data = request.get_json() or {}
    product_id = data.get('product_id', type=int)
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return error_response('產品ID不能為空', 400)
    
    success, message = CartService.add_item(product_id, quantity)
    
    if success:
        return success_response(None, message)
    else:
        return error_response(message, 400)

@api_bp.route('/cart/update', methods=['PUT'])
def update_cart_item():
    """
    Update cart item quantity.
    
    Request body:
        {
            "product_id": int,
            "quantity": int
        }
    
    Returns:
        JSON response confirming update
    """
    data = request.get_json() or {}
    product_id = data.get('product_id', type=int)
    quantity = data.get('quantity', type=int)
    
    if not product_id or quantity is None:
        return error_response('產品ID和數量不能為空', 400)
    
    if quantity == 0:
        return remove_from_cart(product_id)
    
    success, message = CartService.update_item(product_id, quantity)
    
    if success:
        return success_response(None, message)
    else:
        return error_response(message, 400)

@api_bp.route('/cart/remove/<int:product_id>', methods=['DELETE'])
def remove_from_cart(product_id):
    """
    Remove item from cart.
    
    Args:
        product_id: Product ID
        
    Returns:
        JSON response confirming removal
    """
    if CartService.remove_item(product_id):
        return success_response(None, '商品已從購物車移除')
    else:
        return error_response('商品不在購物車中', 404)

@api_bp.route('/cart/clear', methods=['DELETE'])
def clear_cart():
    """
    Clear shopping cart.
    
    Returns:
        JSON response confirming cart cleared
    """
    CartService.clear_cart()
    return success_response(None, '購物車已清空')

