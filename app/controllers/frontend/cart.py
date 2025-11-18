from flask import render_template, request, redirect, url_for, flash
from app.controllers.frontend import frontend_bp
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.constants import FLASH_SUCCESS, FLASH_ERROR, FLASH_WARNING

@frontend_bp.route('/cart/add', methods=['POST'])
def cart_add():
    """Add product to cart"""
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    
    success, message = CartService.add_item(product_id, quantity)
    
    flash(message, FLASH_SUCCESS if success else FLASH_ERROR)
    return redirect(request.referrer or url_for('frontend.product_list'))

@frontend_bp.route('/cart')
def cart():
    """Shopping cart page"""
    cart_items = CartService.get_cart_items()
    total = CartService.calculate_total(cart_items)
    
    return render_template('frontend/cart/cart.html', cart_items=cart_items, total=total)

@frontend_bp.route('/cart/update', methods=['POST'])
def cart_update():
    """Update cart item quantity"""
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', type=int)
    
    if not product_id or not quantity:
        flash('Invalid request', FLASH_ERROR)
        return redirect(url_for('frontend.cart'))
    
    if quantity == 0:
        return redirect(url_for('frontend.cart_remove', product_id=product_id))
    
    success, message = CartService.update_item(product_id, quantity)
    flash(message, FLASH_SUCCESS if success else FLASH_ERROR)
    
    return redirect(url_for('frontend.cart'))

@frontend_bp.route('/cart/remove/<product_id>', methods=['POST', 'GET'])
def cart_remove(product_id):
    """Remove item from cart"""
    if CartService.remove_item(product_id):
        flash('Item removed from cart', FLASH_SUCCESS)
    else:
        flash('Item not found in cart', FLASH_WARNING)
    
    return redirect(url_for('frontend.cart'))

@frontend_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout page"""
    if CartService.is_empty():
        flash('Your cart is empty', FLASH_WARNING)
        return redirect(url_for('frontend.cart'))
    
    if request.method == 'POST':
        # Get shipping information
        shipping_name = request.form.get('shipping_name', '').strip()
        shipping_phone = request.form.get('shipping_phone', '').strip()
        shipping_email = request.form.get('shipping_email', '').strip()
        shipping_address = request.form.get('shipping_address', '').strip()
        
        # Validate required fields
        if not shipping_name or not shipping_phone or not shipping_address:
            flash('Please fill in all required fields', FLASH_ERROR)
            return redirect(url_for('frontend.checkout'))
        
        # Create order using service
        order, error = OrderService.create_order(
            shipping_name=shipping_name,
            shipping_phone=shipping_phone,
            shipping_email=shipping_email if shipping_email else None,
            shipping_address=shipping_address
        )
        
        if error:
            flash(error, FLASH_ERROR)
            return redirect(url_for('frontend.cart'))
        
        # Clear cart
        CartService.clear_cart()
        
        flash('Order placed successfully!', FLASH_SUCCESS)
        return redirect(url_for('frontend.order_complete', order_id=order.id))
    
    # GET request - show checkout form
    cart_items = CartService.get_cart_items()
    total = CartService.calculate_total(cart_items)
    
    return render_template('frontend/cart/checkout.html', cart_items=cart_items, total=total)

@frontend_bp.route('/order-complete/<int:order_id>')
def order_complete(order_id):
    """Order completion page"""
    from app.models import Order
    order = Order.query.get_or_404(order_id)
    return render_template('frontend/cart/order_complete.html', order=order)

