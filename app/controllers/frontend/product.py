"""
Frontend product controller.
Uses API service layer exclusively (all data from API).
"""
from flask import render_template, request, abort
from app.controllers.frontend import frontend_bp
from app.utils.api_service import APIService

@frontend_bp.route('/products')
def product_list():
    """
    Product listing page.
    
    Uses API service layer to fetch products.
    Categories are provided via context processor.
    """
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', 'newest')  # newest, price_asc, price_desc, name
    
    # Fetch products using API service
    # Categories are available via context processor as 'global_categories'
    products_response = APIService.get_products(
        page=page,
        per_page=12,
        category_id=category_id,
        search=search,
        is_active=True,
        sort=sort
    )
    
    if not products_response.get('success'):
        abort(500)
    
    products_data = products_response.get('data', [])
    pagination_info = products_response.get('pagination', {})
    
    # Create pagination-like object for template
    class Pagination:
        def __init__(self, items, page, per_page, total, pages):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = pages
            self.has_prev = page > 1
            self.has_next = page < pages
            self.prev_num = page - 1 if page > 1 else None
            self.next_num = page + 1 if page < pages else None
        
        def iter_pages(self, left_edge=2, right_edge=2, left_current=2, right_current=2):
            """
            Generate page numbers for pagination.
            Similar to Flask-SQLAlchemy's pagination.iter_pages()
            
            Args:
                left_edge: Number of pages on the left edge
                right_edge: Number of pages on the right edge
                left_current: Number of pages on the left of current page
                right_current: Number of pages on the right of current page
            
            Yields:
                Page numbers or None (for ellipsis)
            """
            last = self.pages
            if last == 0:
                return
            
            # Calculate the range of pages to show around current page
            left_start = max(1, self.page - left_current)
            right_end = min(last, self.page + right_current)
            
            # Yield left edge pages
            for num in range(1, min(left_edge + 1, left_start)):
                yield num
            
            # Add ellipsis if there's a gap between left edge and current range
            if left_start > left_edge + 1:
                yield None
            
            # Yield pages around current page
            for num in range(left_start, right_end + 1):
                yield num
            
            # Add ellipsis if there's a gap between current range and right edge
            if right_end < last - right_edge:
                yield None
            
            # Yield right edge pages
            for num in range(max(right_end + 1, last - right_edge + 1), last + 1):
                yield num
    
    products = Pagination(
        items=products_data,
        page=pagination_info.get('page', 1),
        per_page=pagination_info.get('per_page', 12),
        total=pagination_info.get('total', 0),
        pages=pagination_info.get('pages', 0)
    )
    
    return render_template('product/list.html', 
                         products=products,
                         category_id=category_id,
                         search=search,
                         sort=sort)

@frontend_bp.route('/products/<int:id>')
@frontend_bp.route('/products/<int:id>/<slug>')
def product_detail(id, slug=None):
    """
    Product detail page.
    
    Uses API service layer to fetch product and related products.
    Categories are provided via context processor.
    """
    # Fetch product and related products using API service
    product_response = APIService.get_product(id)
    
    if not product_response.get('success'):
        abort(404)
    
    product_data = product_response.get('data', {})
    
    if not product_data.get('is_active'):
        abort(404)
    
    # Fetch related products
    # Categories are available via context processor as 'global_categories'
    related_response = APIService.get_related_products(
        product_id=id,
        category_id=product_data.get('category_id'),
        limit=4
    )
    
    related_products_data = related_response.get('data', []) if related_response.get('success') else []
    
    return render_template('product/detail.html',
                         product=product_data,
                         related_products=related_products_data)
