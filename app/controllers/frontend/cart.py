from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app.controllers.frontend import frontend_bp
from app.models import Product, Order, OrderItem
from app import db
from decimal import Decimal

def get_cart():
    """Get cart from session"""
    return session.get('cart', {})

def save_cart(cart):
    """Save cart to session"""
    session['cart'] = cart
    session.modified = True

def add_to_cart(product_id, quantity=1):
    """Add product to cart"""
    product = Product.query.get_or_404(product_id)
    
    if not product.is_active or product.stock < quantity:
        return False, "Product not available"
    
    cart = get_cart()
    
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)] = {
            'quantity': quantity,
            'price': float(product.price),
            'name': product.name,
            'image': product.get_main_image()
        }
    
    save_cart(cart)
    return True, "Product added to cart"

@frontend_bp.route('/cart/add', methods=['POST'])
def cart_add():
    """Add product to cart"""
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    
    success, message = add_to_cart(product_id, quantity)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(request.referrer or url_for('frontend.product_list'))

@frontend_bp.route('/cart')
def cart():
    """Shopping cart page"""
    cart = get_cart()
    cart_items = []
    total = 0
    
    for product_id, item in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            quantity = item['quantity']
            price = float(product.price)
            subtotal = price * quantity
            total += subtotal
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
    
    return render_template('frontend/cart/cart.html', cart_items=cart_items, total=total)

@frontend_bp.route('/cart/update', methods=['POST'])
def cart_update():
    """Update cart item quantity"""
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity', type=int)
    
    cart = get_cart()
    
    if product_id and str(product_id) in cart and quantity > 0:
        product = Product.query.get(int(product_id))
        if product and product.stock >= quantity:
            cart[str(product_id)]['quantity'] = quantity
            save_cart(cart)
            flash('Cart updated', 'success')
        else:
            flash('Insufficient stock', 'danger')
    elif quantity == 0:
        return redirect(url_for('frontend.cart_remove', product_id=product_id))
    
    return redirect(url_for('frontend.cart'))

@frontend_bp.route('/cart/remove/<product_id>', methods=['POST', 'GET'])
def cart_remove(product_id):
    """Remove item from cart"""
    cart = get_cart()
    
    if str(product_id) in cart:
        del cart[str(product_id)]
        save_cart(cart)
        flash('Item removed from cart', 'success')
    
    return redirect(url_for('frontend.cart'))

@frontend_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout page"""
    cart = get_cart()
    
    if not cart:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('frontend.cart'))
    
    if request.method == 'POST':
        # Get shipping information
        shipping_name = request.form.get('shipping_name')
        shipping_phone = request.form.get('shipping_phone')
        shipping_email = request.form.get('shipping_email')
        shipping_address = request.form.get('shipping_address')
        
        # Calculate total
        total = 0
        order_items = []
        
        for product_id, item in cart.items():
            product = Product.query.get(int(product_id))
            if product:
                quantity = item['quantity']
                if product.stock < quantity:
                    flash(f'Insufficient stock for {product.name}', 'danger')
                    return redirect(url_for('frontend.cart'))
                
                price = float(product.price)
                subtotal = price * quantity
                total += subtotal
                
                order_items.append({
                    'product': product,
                    'quantity': quantity,
                    'price': price
                })
        
        # Create order
        order = Order(
            order_number=Order.generate_order_number(),
            total_amount=Decimal(str(total)),
            shipping_name=shipping_name,
            shipping_phone=shipping_phone,
            shipping_email=shipping_email,
            shipping_address=shipping_address,
            status='pending'
        )
        
        db.session.add(order)
        db.session.flush()
        
        # Create order items and update stock
        for item in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price=Decimal(str(item['price']))
            )
            db.session.add(order_item)
            
            # Update product stock
            item['product'].stock -= item['quantity']
        
        db.session.commit()
        
        # Clear cart
        session.pop('cart', None)
        session.modified = True
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('frontend.order_complete', order_id=order.id))
    
    # Calculate cart total
    cart_items = []
    total = 0
    
    for product_id, item in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            quantity = item['quantity']
            price = float(product.price)
            subtotal = price * quantity
            total += subtotal
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
    
    return render_template('frontend/cart/checkout.html', cart_items=cart_items, total=total)

@frontend_bp.route('/order-complete/<int:order_id>')
def order_complete(order_id):
    """Order completion page"""
    order = Order.query.get_or_404(order_id)
    return render_template('frontend/cart/order_complete.html', order=order)

