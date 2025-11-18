"""
Orders API endpoints.
"""
from flask import request
from app.controllers.api import api_bp
from app.utils.api_auth import api_login_required
from app.utils.api_response import success_response, error_response, paginated_response
from app.models import Order, OrderItem
from app import db
from app.services.order_service import OrderService
from sqlalchemy.orm import joinedload

@api_bp.route('/orders', methods=['GET'])
@api_login_required
def get_orders():
    """
    Get list of orders.
    
    Query params:
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
        status: Filter by order status
    
    Returns:
        JSON response with paginated orders list
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '').strip()
    
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
            'shipping_phone': order.shipping_phone,
            'shipping_email': order.shipping_email,
            'shipping_address': order.shipping_address,
            'created_at': order.created_at.isoformat()
        })
    
    return paginated_response(
        orders_data, page, per_page, pagination.total, '訂單列表'
    )

@api_bp.route('/orders', methods=['POST'])
def create_order():
    """
    Create new order from cart.
    
    Request body:
        {
            "shipping_name": "string",
            "shipping_phone": "string",
            "shipping_email": "string" (optional),
            "shipping_address": "string",
            "notes": "string" (optional)
        }
    
    Returns:
        JSON response with created order data
    """
    data = request.get_json() or {}
    
    shipping_name = data.get('shipping_name', '').strip()
    shipping_phone = data.get('shipping_phone', '').strip()
    shipping_email = data.get('shipping_email', '').strip() or None
    shipping_address = data.get('shipping_address', '').strip()
    notes = data.get('notes', '').strip() or None
    
    # Validation
    if not shipping_name or not shipping_phone or not shipping_address:
        return error_response('請填寫所有必填欄位', 400)
    
    # Create order using service
    order, error = OrderService.create_order(
        shipping_name=shipping_name,
        shipping_phone=shipping_phone,
        shipping_email=shipping_email,
        shipping_address=shipping_address
    )
    
    if error:
        return error_response(error, 400)
    
    order_data = {
        'id': order.id,
        'order_number': order.order_number,
        'total_amount': float(order.total_amount),
        'status': order.status,
        'created_at': order.created_at.isoformat()
    }
    
    return success_response(order_data, '訂單建立成功', 201)

@api_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """
    Get order by ID.
    
    Args:
        order_id: Order ID
        
    Returns:
        JSON response with order data including items
    """
    order = db.session.query(Order)\
        .options(
            joinedload(Order.items).joinedload(OrderItem.product)
        )\
        .filter_by(id=order_id)\
        .first()
    
    if not order:
        return error_response('訂單不存在', 404)
    
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
        'notes': order.notes,
        'items': items_data,
        'created_at': order.created_at.isoformat(),
        'updated_at': order.updated_at.isoformat()
    }
    return success_response(order_data)

@api_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@api_login_required
def update_order_status(order_id):
    """
    Update order status.
    
    Args:
        order_id: Order ID
        
    Request body:
        {
            "status": "pending|processing|shipped|delivered|cancelled"
        }
    
    Returns:
        JSON response with updated order data
    """
    data = request.get_json() or {}
    new_status = data.get('status', '').strip()
    
    if not new_status:
        return error_response('請選擇訂單狀態', 400)
    
    success, error = OrderService.update_status(order_id, new_status)
    
    if success:
        order = Order.query.get(order_id)
        order_data = {
            'id': order.id,
            'order_number': order.order_number,
            'status': order.status
        }
        return success_response(order_data, '訂單狀態更新成功')
    else:
        return error_response(error or '更新訂單狀態失敗', 400)
