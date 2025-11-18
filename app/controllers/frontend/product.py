from flask import render_template, request
from app.controllers.frontend import frontend_bp
from app.models import Product, Category

@frontend_bp.route('/products')
def product_list():
    """Product listing page"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'newest')  # newest, price_asc, price_desc, name
    
    query = Product.query.filter_by(is_active=True)
    
    # Filter by category
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # Search
    if search:
        query = query.filter(Product.name.contains(search))
    
    # Sorting
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'name':
        query = query.order_by(Product.name.asc())
    else:  # newest
        query = query.order_by(Product.created_at.desc())
    
    products = query.paginate(page=page, per_page=12, error_out=False)
    
    # Get categories for sidebar
    categories = Category.query.filter_by(is_active=True, parent_id=None).all()
    
    return render_template('product/list.html', 
                         products=products,
                         categories=categories,
                         category_id=category_id,
                         search=search,
                         sort=sort)

@frontend_bp.route('/products/<int:id>')
@frontend_bp.route('/products/<int:id>/<slug>')
def product_detail(id, slug=None):
    """Product detail page"""
    product = Product.query.get_or_404(id)
    
    if not product.is_active:
        from flask import abort
        abort(404)
    
    # Get related products (same category)
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_active == True
    ).limit(4).all()
    
    # Get categories for sidebar
    categories = Category.query.filter_by(is_active=True, parent_id=None).all()
    
    return render_template('product/detail.html',
                         product=product,
                         related_products=related_products,
                         categories=categories)

