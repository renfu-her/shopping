"""
Cart service for handling shopping cart operations
"""
from typing import List, Dict, Tuple, Optional
from flask import session
from app.models import Product
from decimal import Decimal


class CartService:
    """Service for managing shopping cart operations"""
    
    @staticmethod
    def get_cart() -> Dict:
        """Get cart from session"""
        return session.get('cart', {})
    
    @staticmethod
    def save_cart(cart: Dict) -> None:
        """Save cart to session"""
        session['cart'] = cart
        session.modified = True
    
    @staticmethod
    def add_item(product_id: int, quantity: int = 1) -> Tuple[bool, str]:
        """
        Add product to cart
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        product = Product.query.get_or_404(product_id)
        
        if not product.is_active:
            return False, "Product is not available"
        
        if product.stock < quantity:
            return False, "Insufficient stock"
        
        cart = CartService.get_cart()
        product_key = str(product_id)
        
        if product_key in cart:
            new_quantity = cart[product_key]['quantity'] + quantity
            if product.stock < new_quantity:
                return False, "Insufficient stock"
            cart[product_key]['quantity'] = new_quantity
        else:
            cart[product_key] = {
                'quantity': quantity,
                'price': float(product.price),
                'name': product.name,
                'image': product.get_main_image()
            }
        
        CartService.save_cart(cart)
        return True, "Product added to cart"
    
    @staticmethod
    def update_item(product_id: int, quantity: int) -> Tuple[bool, str]:
        """
        Update cart item quantity
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        
        cart = CartService.get_cart()
        product_key = str(product_id)
        
        if product_key not in cart:
            return False, "Item not found in cart"
        
        product = Product.query.get(product_id)
        if not product:
            return False, "Product not found"
        
        if product.stock < quantity:
            return False, "Insufficient stock"
        
        cart[product_key]['quantity'] = quantity
        CartService.save_cart(cart)
        return True, "Cart updated"
    
    @staticmethod
    def remove_item(product_id: int) -> bool:
        """Remove item from cart"""
        cart = CartService.get_cart()
        product_key = str(product_id)
        
        if product_key in cart:
            del cart[product_key]
            CartService.save_cart(cart)
            return True
        return False
    
    @staticmethod
    def get_cart_items() -> List[Dict]:
        """
        Get cart items with product details
        
        Returns:
            List of dicts with product, quantity, and subtotal
        """
        cart = CartService.get_cart()
        cart_items = []
        
        for product_id, item in cart.items():
            product = Product.query.get(int(product_id))
            if product:
                quantity = item['quantity']
                price = float(product.price)
                subtotal = price * quantity
                
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
        
        return cart_items
    
    @staticmethod
    def calculate_total(cart_items: Optional[List[Dict]] = None) -> Decimal:
        """
        Calculate total cart value
        
        Args:
            cart_items: Optional list of cart items. If None, fetches from cart.
        
        Returns:
            Total amount as Decimal
        """
        if cart_items is None:
            cart_items = CartService.get_cart_items()
        
        total = sum(item['subtotal'] for item in cart_items)
        return Decimal(str(total))
    
    @staticmethod
    def clear_cart() -> None:
        """Clear all items from cart"""
        session.pop('cart', None)
        session.modified = True
    
    @staticmethod
    def is_empty() -> bool:
        """Check if cart is empty"""
        return len(CartService.get_cart()) == 0

