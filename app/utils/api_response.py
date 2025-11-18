"""
Unified API response utilities for consistent API responses.
"""
from flask import jsonify
from typing import Any, Optional, Dict

def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> tuple:
    """
    Create a success API response.
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
        
    Returns:
        Tuple of (jsonify response, status_code)
    """
    response = {
        'success': True,
        'message': message,
        'data': data
    }
    return jsonify(response), status_code

def error_response(message: str = "Error", status_code: int = 400, errors: Optional[Dict] = None) -> tuple:
    """
    Create an error API response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        errors: Optional dictionary of field-specific errors
        
    Returns:
        Tuple of (jsonify response, status_code)
    """
    response = {
        'success': False,
        'message': message,
        'errors': errors or {}
    }
    return jsonify(response), status_code

def paginated_response(data: list, page: int, per_page: int, total: int, 
                      message: str = "Success") -> tuple:
    """
    Create a paginated API response.
    
    Args:
        data: List of items for current page
        page: Current page number
        per_page: Items per page
        total: Total number of items
        message: Success message
        
    Returns:
        Tuple of (jsonify response, status_code)
    """
    response = {
        'success': True,
        'message': message,
        'data': data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page if total > 0 else 0
        }
    }
    return jsonify(response), 200

