"""
Order service for handling order operations
"""
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from app.models import Order, OrderItem, Product
from app import db
from app.constants import ORDER_STATUS_PENDING


class OrderService:
    """Service for managing order operations"""
    
    @staticmethod
    def create_order(
        shipping_name: str,
        shipping_phone: str,
        shipping_address: str,
        shipping_email: Optional[str] = None,
        cart_items: Optional[List[Dict]] = None
    ) -> Tuple[Order, Optional[str]]:
        """
        Create a new order from cart items
        
        Returns:
            Tuple[Order, Optional[str]]: (order, error_message)
        """
        from app.services.cart_service import CartService
        
        if cart_items is None:
            cart_items = CartService.get_cart_items()
        
        if not cart_items:
            return None, "Cart is empty"
        
        # Validate stock and calculate total
        total = Decimal('0')
        order_items_data = []
        
        for item in cart_items:
            product = item['product']
            quantity = item['quantity']
            
            if product.stock < quantity:
                return None, f'Insufficient stock for {product.name}'
            
            price = Decimal(str(product.price))
            subtotal = price * quantity
            total += subtotal
            
            order_items_data.append({
                'product': product,
                'quantity': quantity,
                'price': price
            })
        
        # Create order
        order = Order(
            order_number=Order.generate_order_number(),
            total_amount=total,
            shipping_name=shipping_name,
            shipping_phone=shipping_phone,
            shipping_email=shipping_email,
            shipping_address=shipping_address,
            status=ORDER_STATUS_PENDING
        )
        
        try:
            db.session.add(order)
            db.session.flush()
            
            # Create order items and update stock
            for item_data in order_items_data:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item_data['product'].id,
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                db.session.add(order_item)
                
                # Update product stock
                item_data['product'].stock -= item_data['quantity']
            
            db.session.commit()
            return order, None
            
        except Exception as e:
            db.session.rollback()
            return None, f"Error creating order: {str(e)}"
    
    @staticmethod
    def update_status(order_id: int, new_status: str) -> Tuple[bool, Optional[str]]:
        """
        Update order status
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        from app.constants import ORDER_STATUS_CHOICES
        
        if new_status not in ORDER_STATUS_CHOICES:
            return False, "Invalid status"
        
        order = Order.query.get_or_404(order_id)
        order.status = new_status
        
        try:
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating order: {str(e)}"

