"""
Validation utilities
"""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number (basic validation)"""
    # Remove spaces, dashes, parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    # Check if it contains only digits and optional + at start
    return bool(re.match(r'^\+?\d{7,15}$', cleaned))


def validate_required(value: Optional[str], field_name: str = 'Field') -> Tuple[bool, Optional[str]]:
    """
    Validate required field
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, f"{field_name} is required"
    return True, None

