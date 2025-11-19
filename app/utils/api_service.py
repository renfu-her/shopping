"""
API service layer - Direct function calls to API logic.
This allows backend/frontend controllers to use API functionality
without making HTTP requests (since they're in the same process).
"""
from typing import Dict, Any, Optional, List
from flask import request as flask_request, session
from app.utils.api_response import success_response, error_response
from app.models import User, Product, Category, Order, Banner
from app import db
from app.services.auth_service import AuthService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.utils.helpers import save_uploaded_file, delete_file, slugify
from sqlalchemy.orm import joinedload
from app.models import OrderItem

class APIService:
    """Service layer that provides API functionality as callable functions."""
    
    @staticmethod
    def get_dashboard_stats() -> Dict[str, Any]:
        """Get dashboard statistics."""
        stats = {
            'total_users': User.query.count(),
            'total_products': Product.query.count(),
            'total_orders': Order.query.count(),
            'total_categories': Category.query.count(),
            'total_banners': Banner.query.count(),
            'pending_orders': Order.query.filter_by(status='pending').count(),
            'active_products': Product.query.filter_by(is_active=True).count(),
        }
        return {'success': True, 'data': stats}
    
    @staticmethod
    def get_recent_orders(limit: int = 10) -> Dict[str, Any]:
        """Get recent orders."""
        orders = db.session.query(Order)\
            .options(
                joinedload(Order.items).joinedload(OrderItem.product)
            )\
            .order_by(Order.created_at.desc())\
            .limit(limit)\
            .all()
        
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.id,
                'order_number': order.order_number,
                'total_amount': float(order.total_amount),
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'shipping_name': order.shipping_name
            })
        
        return {'success': True, 'data': orders_data}
    
    @staticmethod
    def get_users(page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get users list."""
        pagination = User.query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users_data = []
        for user in pagination.items:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at.isoformat()
            })
        
        return {
            'success': True,
            'data': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }
    
    @staticmethod
    def get_products(page: int = 1, per_page: int = 20, 
                    category_id: Optional[int] = None,
                    search: Optional[str] = None,
                    is_active: Optional[bool] = None,
                    sort: Optional[str] = None) -> Dict[str, Any]:
        """
        Get products list.
        
        Args:
            page: Page number
            per_page: Items per page
            category_id: Filter by category
            search: Search in product name
            is_active: Filter by active status
            sort: Sort option (newest, price_asc, price_desc, name)
        """
        query = db.session.query(Product).options(joinedload(Product.category))
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        if search:
            query = query.filter(Product.name.contains(search))
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        # Sorting
        if sort == 'price_asc':
            query = query.order_by(Product.price.asc())
        elif sort == 'price_desc':
            query = query.order_by(Product.price.desc())
        elif sort == 'name':
            query = query.order_by(Product.name.asc())
        else:  # newest
            query = query.order_by(Product.created_at.desc())
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        products_data = []
        for product in pagination.items:
            images = product.get_images()
            products_data.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'description': product.description,
                'price': float(product.price),
                'stock': product.stock,
                'category_id': product.category_id,
                'category_name': product.category.name if product.category else None,
                'images': images,
                'main_image': images[0] if images else '/static/images/no-image.png',
                'is_active': product.is_active,
                'is_in_stock': product.is_in_stock(),
                'created_at': product.created_at.isoformat()
            })
        
        return {
            'success': True,
            'data': products_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }
    
    @staticmethod
    def get_product(product_id: int) -> Dict[str, Any]:
        """Get product by ID."""
        product = db.session.query(Product)\
            .options(joinedload(Product.category))\
            .get(product_id)
        
        if not product:
            return {'success': False, 'message': 'Product not found'}
        
        images = product.get_images()
        product_data = {
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'description': product.description,
            'price': float(product.price),
            'stock': product.stock,
            'category_id': product.category_id,
            'category_name': product.category.name if product.category else None,
            'images': images,
            'main_image': images[0] if images else '/static/images/no-image.png',
            'is_active': product.is_active,
            'is_in_stock': product.is_in_stock(),
            'created_at': product.created_at.isoformat(),
            'updated_at': product.updated_at.isoformat()
        }
        return {'success': True, 'data': product_data}
    
    @staticmethod
    def get_related_products(product_id: int, category_id: int, limit: int = 4) -> Dict[str, Any]:
        """Get related products (same category)."""
        products = db.session.query(Product)\
            .options(joinedload(Product.category))\
            .filter(
                Product.category_id == category_id,
                Product.id != product_id,
                Product.is_active == True
            )\
            .limit(limit)\
            .all()
        
        products_data = []
        for product in products:
            images = product.get_images()
            products_data.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'price': float(product.price),
                'images': images,
                'main_image': images[0] if images else '/static/images/no-image.png',
                'is_active': product.is_active,
                'is_in_stock': product.is_in_stock()
            })
        
        return {'success': True, 'data': products_data}
    
    @staticmethod
    def get_categories(parent_id: Optional[int] = None,
                      is_active: Optional[bool] = None) -> Dict[str, Any]:
        """Get categories list."""
        query = Category.query
        
        if parent_id is not None:
            query = query.filter_by(parent_id=parent_id)
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        categories = query.order_by(Category.sort_order, Category.id).all()
        
        categories_data = []
        for category in categories:
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'parent_id': category.parent_id,
                'parent_name': category.parent.name if category.parent else None,
                'description': category.description,
                'image': category.image,
                'sort_order': category.sort_order,
                'is_active': category.is_active,
                'children_count': len(category.children) if category.children else 0
            })
        
        return {'success': True, 'data': categories_data}
    
    @staticmethod
    def get_category(category_id: int) -> Dict[str, Any]:
        """Get category by ID."""
        category = Category.query.get(category_id)
        if not category:
            return {'success': False, 'message': 'Category not found'}
        
        category_data = {
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'parent_id': category.parent_id,
            'parent_name': category.parent.name if category.parent else None,
            'description': category.description,
            'image': category.image,
            'sort_order': category.sort_order,
            'is_active': category.is_active,
            'children': [{'id': c.id, 'name': c.name} for c in category.children]
        }
        return {'success': True, 'data': category_data}
    
    @staticmethod
    def get_orders(page: int = 1, per_page: int = 20,
                  status: Optional[str] = None) -> Dict[str, Any]:
        """Get orders list."""
        query = db.session.query(Order).options(joinedload(Order.items))
        
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        orders_data = []
        for order in pagination.items:
            orders_data.append({
                'id': order.id,
                'order_number': order.order_number,
                'total_amount': float(order.total_amount),
                'status': order.status,
                'shipping_name': order.shipping_name,
                'created_at': order.created_at.isoformat()
            })
        
        return {
            'success': True,
            'data': orders_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }
    
    @staticmethod
    def get_order(order_id: int) -> Dict[str, Any]:
        """Get order by ID."""
        order = db.session.query(Order)\
            .options(
                joinedload(Order.items).joinedload(OrderItem.product)
            )\
            .filter_by(id=order_id)\
            .first()
        
        if not order:
            return {'success': False, 'message': 'Order not found'}
        
        items_data = []
        for item in order.items:
            items_data.append({
                'id': item.id,
                'product_id': item.product_id,
                'product_name': item.product.name if item.product else 'N/A',
                'quantity': item.quantity,
                'price': float(item.price),
                'subtotal': float(item.get_subtotal())
            })
        
        order_data = {
            'id': order.id,
            'order_number': order.order_number,
            'total_amount': float(order.total_amount),
            'status': order.status,
            'shipping_name': order.shipping_name,
            'shipping_phone': order.shipping_phone,
            'shipping_email': order.shipping_email,
            'shipping_address': order.shipping_address,
            'items': items_data,
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat()
        }
        
        return {'success': True, 'data': order_data}
    
    @staticmethod
    def create_order(shipping_name: str, shipping_phone: str,
                    shipping_email: Optional[str] = None,
                    shipping_address: str = '',
                    notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Create new order from cart.
        
        Returns:
            Dict with 'success', 'data' (order data), and optional 'message'
        """
        # Validation
        if not shipping_name or not shipping_phone or not shipping_address:
            return {'success': False, 'message': '請填寫所有必填欄位'}
        
        # Create order using service
        order, error = OrderService.create_order(
            shipping_name=shipping_name,
            shipping_phone=shipping_phone,
            shipping_email=shipping_email,
            shipping_address=shipping_address
        )
        
        if error:
            return {'success': False, 'message': error}
        
        order_data = {
            'id': order.id,
            'order_number': order.order_number,
            'total_amount': float(order.total_amount),
            'status': order.status,
            'created_at': order.created_at.isoformat()
        }
        
        return {'success': True, 'data': order_data, 'message': '訂單建立成功'}
    
    @staticmethod
    def get_banners(is_active: Optional[bool] = None) -> Dict[str, Any]:
        """Get banners list."""
        query = Banner.query
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        banners = query.order_by(Banner.sort_order).all()
        
        banners_data = []
        for banner in banners:
            banners_data.append({
                'id': banner.id,
                'title': banner.title,
                'link': banner.link,
                'image': banner.image,
                'sort_order': banner.sort_order,
                'is_active': banner.is_active
            })
        
        return {'success': True, 'data': banners_data}
    
    # Cart API methods
    @staticmethod
    def get_cart() -> Dict[str, Any]:
        """Get shopping cart items."""
        cart_items = CartService.get_cart_items()
        total = CartService.calculate_total(cart_items)
        
        # Convert cart items to dict format
        items_data = []
        for item in cart_items:
            product = item.get('product')
            if product:
                images = product.get_images()
                items_data.append({
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                        'stock': product.stock,
                        'main_image': images[0] if images else '/static/images/no-image.png',
                        'is_in_stock': product.is_in_stock()
                    },
                    'quantity': item.get('quantity', 0),
                    'subtotal': float(item.get('subtotal', 0))
                })
            else:
                items_data.append({
                    'product': {
                        'id': None,
                        'name': 'N/A',
                        'price': 0,
                        'stock': 0,
                        'main_image': None,
                        'is_in_stock': False
                    },
                    'quantity': item.get('quantity', 0),
                    'subtotal': float(item.get('subtotal', 0))
                })
        
        return {
            'success': True,
            'data': {
                'items': items_data,
                'total': float(total),
                'item_count': len(cart_items)
            }
        }
    
    @staticmethod
    def add_to_cart(product_id: int, quantity: int = 1) -> Dict[str, Any]:
        """Add product to cart."""
        if not product_id:
            return {'success': False, 'message': '產品ID不能為空'}
        
        success, message = CartService.add_item(product_id, quantity)
        
        if success:
            return {'success': True, 'message': message}
        else:
            return {'success': False, 'message': message}
    
    @staticmethod
    def update_cart_item(product_id: int, quantity: int) -> Dict[str, Any]:
        """Update cart item quantity."""
        if not product_id or quantity is None:
            return {'success': False, 'message': '產品ID和數量不能為空'}
        
        if quantity == 0:
            return APIService.remove_from_cart(product_id)
        
        success, message = CartService.update_item(product_id, quantity)
        
        if success:
            return {'success': True, 'message': message}
        else:
            return {'success': False, 'message': message}
    
    @staticmethod
    def remove_from_cart(product_id: int) -> Dict[str, Any]:
        """Remove item from cart."""
        if CartService.remove_item(product_id):
            return {'success': True, 'message': '商品已從購物車移除'}
        else:
            return {'success': False, 'message': '商品不在購物車中'}
    
    @staticmethod
    def clear_cart() -> Dict[str, Any]:
        """Clear shopping cart."""
        CartService.clear_cart()
        return {'success': True, 'message': '購物車已清空'}
    
    @staticmethod
    def is_cart_empty() -> bool:
        """Check if cart is empty."""
        return CartService.is_empty()
