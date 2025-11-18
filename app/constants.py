"""
Application-wide constants
"""
# Order Status
ORDER_STATUS_PENDING = 'pending'
ORDER_STATUS_PROCESSING = 'processing'
ORDER_STATUS_SHIPPED = 'shipped'
ORDER_STATUS_DELIVERED = 'delivered'
ORDER_STATUS_CANCELLED = 'cancelled'

ORDER_STATUS_CHOICES = [
    ORDER_STATUS_PENDING,
    ORDER_STATUS_PROCESSING,
    ORDER_STATUS_SHIPPED,
    ORDER_STATUS_DELIVERED,
    ORDER_STATUS_CANCELLED,
]

# User Roles
USER_ROLE_ADMIN = 'admin'
USER_ROLE_CUSTOMER = 'customer'

USER_ROLES = [USER_ROLE_ADMIN, USER_ROLE_CUSTOMER]

# Product Sorting Options
SORT_NEWEST = 'newest'
SORT_PRICE_ASC = 'price_asc'
SORT_PRICE_DESC = 'price_desc'
SORT_NAME = 'name'

SORT_OPTIONS = {
    SORT_NEWEST: 'Newest',
    SORT_PRICE_ASC: 'Price: Low to High',
    SORT_PRICE_DESC: 'Price: High to Low',
    SORT_NAME: 'Name',
}

# Pagination
PRODUCTS_PER_PAGE_FRONTEND = 12
PRODUCTS_PER_PAGE_ADMIN = 20
ORDERS_PER_PAGE_ADMIN = 20
USERS_PER_PAGE_ADMIN = 20

# Flash Message Categories
FLASH_SUCCESS = 'success'
FLASH_ERROR = 'danger'
FLASH_WARNING = 'warning'
FLASH_INFO = 'info'

