"""
Frontend cart controller.
Uses API service layer exclusively (all operations through API).
"""
from flask import render_template, request, redirect, url_for, flash, abort
from app.controllers.frontend import frontend_bp
from app.utils.api_service import APIService
from app.constants import FLASH_SUCCESS, FLASH_ERROR, FLASH_WARNING

@frontend_bp.route('/cart/add', methods=['POST'])
def cart_add():
    """
    Add product to cart.
    
    Uses API service layer.
    """
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    
    # Use API service
    response = APIService.add_to_cart(product_id, quantity)
    
    if response.get('success'):
        flash(response.get('message', '商品已加入購物車'), FLASH_SUCCESS)
    else:
        flash(response.get('message', '加入購物車失敗'), FLASH_ERROR)
    
    return redirect(request.referrer or url_for('frontend.product_list'))

@frontend_bp.route('/cart')
def cart():
    """
    Shopping cart page.
    
    Uses API service layer to get cart data.
    """
    # Get cart from API service
    cart_response = APIService.get_cart()
    
    if not cart_response.get('success'):
        cart_data = {'items': [], 'total': 0, 'item_count': 0}
    else:
        cart_data = cart_response.get('data', {})
    
    cart_items = cart_data.get('items', [])
    total = cart_data.get('total', 0)
    
    return render_template('cart/cart.html', cart_items=cart_items, total=total)

@frontend_bp.route('/cart/update', methods=['POST'])
def cart_update():
    """
    Update cart item quantity.
    
    Uses API service layer.
    """
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', type=int)
    
    if not product_id or not quantity:
        flash('無效的請求', FLASH_ERROR)
        return redirect(url_for('frontend.cart'))
    
    if quantity == 0:
        return redirect(url_for('frontend.cart_remove', product_id=product_id))
    
    # Use API service
    response = APIService.update_cart_item(product_id, quantity)
    
    if response.get('success'):
        flash(response.get('message', '購物車已更新'), FLASH_SUCCESS)
    else:
        flash(response.get('message', '更新購物車失敗'), FLASH_ERROR)
    
    return redirect(url_for('frontend.cart'))

@frontend_bp.route('/cart/remove/<product_id>', methods=['POST', 'GET'])
def cart_remove(product_id):
    """
    Remove item from cart.
    
    Uses API service layer.
    """
    # Use API service
    response = APIService.remove_from_cart(product_id)
    
    if response.get('success'):
        flash(response.get('message', '商品已從購物車移除'), FLASH_SUCCESS)
    else:
        flash(response.get('message', '移除商品失敗'), FLASH_WARNING)
    
    return redirect(url_for('frontend.cart'))

@frontend_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """
    Checkout page.
    
    Uses API service layer for all operations.
    Optimized to avoid duplicate cart API calls.
    """
    if request.method == 'POST':
        # Get shipping information
        shipping_name = request.form.get('shipping_name', '').strip()
        shipping_phone = request.form.get('shipping_phone', '').strip()
        shipping_email = request.form.get('shipping_email', '').strip()
        shipping_address = request.form.get('shipping_address', '').strip()
        
        # Validate required fields
        if not shipping_name or not shipping_phone or not shipping_address:
            flash('請填寫所有必填欄位', FLASH_ERROR)
            return redirect(url_for('frontend.checkout'))
        
        # Check if cart is empty before creating order
        if APIService.is_cart_empty():
            flash('購物車是空的', FLASH_WARNING)
            return redirect(url_for('frontend.cart'))
        
        # Create order via API service
        order_response = APIService.create_order(
            shipping_name=shipping_name,
            shipping_phone=shipping_phone,
            shipping_email=shipping_email if shipping_email else None,
            shipping_address=shipping_address
        )
        
        if order_response.get('success'):
            order_data = order_response.get('data', {})
            order_id = order_data.get('id')
            
            # Clear cart via API service
            APIService.clear_cart()
            
            flash('訂單建立成功！', FLASH_SUCCESS)
            return redirect(url_for('frontend.order_complete', order_id=order_id))
        else:
            flash(order_response.get('message', '建立訂單失敗'), FLASH_ERROR)
            return redirect(url_for('frontend.cart'))
    
    # GET request - show checkout form
    # Check if cart is empty first
    if APIService.is_cart_empty():
        flash('購物車是空的', FLASH_WARNING)
        return redirect(url_for('frontend.cart'))
    
    # Get cart data
    cart_response = APIService.get_cart()
    cart_data = cart_response.get('data', {}) if cart_response.get('success') else {}
    cart_items = cart_data.get('items', [])
    total = cart_data.get('total', 0)
    
    return render_template('cart/checkout.html', cart_items=cart_items, total=total)

@frontend_bp.route('/order-complete/<int:order_id>')
def order_complete(order_id):
    """
    Order completion page.
    
    Uses API service layer to get order data.
    """
    # Get order from API service
    order_response = APIService.get_order(order_id)
    
    if not order_response.get('success'):
        abort(404)
    
    order_data = order_response.get('data', {})
    
    return render_template('cart/order_complete.html', order=order_data)
