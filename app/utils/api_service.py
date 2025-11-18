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
from app.utils.helpers import save_uploaded_file, delete_file, slugify
from sqlalchemy.orm import joinedload
from app.models import OrderItem
from app.services.order_service import OrderService

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
                    is_active: Optional[bool] = None) -> Dict[str, Any]:
        """Get products list."""
        query = db.session.query(Product).options(joinedload(Product.category))
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        if search:
            query = query.filter(Product.name.contains(search))
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        pagination = query.order_by(Product.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        products_data = []
        for product in pagination.items:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'price': float(product.price),
                'stock': product.stock,
                'category_id': product.category_id,
                'category_name': product.category.name if product.category else None,
                'is_active': product.is_active
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
                'is_active': category.is_active
            })
        
        return {'success': True, 'data': categories_data}
    
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
            'created_at': order.created_at.isoformat()
        }
        
        return {'success': True, 'data': order_data}
    
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

