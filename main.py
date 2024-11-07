from flask import abort, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, LoginManager, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv
from forms import *
from model import *
from payment import *
from database import create_app
import os
from werkzeug.utils import secure_filename

app = create_app()
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)        
    return decorated_function


# -------------------------------------------------------------#
# -------------------------USER------------------------------- #
# -------------------------------------------------------------#

@app.route('/')
def home():
    print("Hello")
    products = Product.query.all()
    
    return render_template('index.html', products= products)
    # return 1

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUp()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )

        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hashed_password,
            
            street=form.street.data,
            city=form.city.data,
            state=form.state.data,
            postal_code=form.postal_code.data,
            country=form.country.data,
            phone_number=form.phone_number.data
        )

        db.session.add(new_user)
        db.session.commit()

        # new_address = Address(
        #     user_id=new_user.id,
        #     street=form.street.data,
        #     city=form.city.data,
        #     state=form.state.data,
        #     zip_code=form.postal_code.data,
        #     country=form.country.data,
        #     phone_number=form.phone_number.data
        # )

        # db.session.add(new_address)
        # db.session.commit()  # Commit the address

        login_user(new_user)
        flash('Account created and logged in successfully!', 'success')
        return redirect(url_for('home')) 
    
    return render_template('signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        
    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id) 
    return render_template('product_detail.html', product=product)

# -------------------------------------------------------------#
# ---------------------USER - CART---------------------------- #
# -------------------------------------------------------------#

@app.route('/cart')
def cart():
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('home'))
    
    total_amount = 0
    order = None

    for product_id, quantity in session['cart'].items():
        product = Product.query.get(product_id)
        if product:
            cart_items = CartItem(
                product_id= product.id,
                quantity =  quantity,
                total_amount =  product.price * quantity
            )
            
            
            
    # if current_user.is_authenticated:
    #     order = Order(user_id=current_user.id, total_amount=total_amount, status='pending')
    #     db.session.add(order)
    #     db.session.commit() 
        
    #     for item in cart_items:
    #         order_item = OrderItem(order_id=order.id, product_id=item['product'].id, quantity=item['quantity'], price=item['product'].price)
    #         db.session.add(order_item)
            
    #     db.session.commit()
        
    #     return redirect(url_for('create_checkout', order_id=order.id))
    
    return render_template('cart.html', cart_items=cart_items, total_amount=total_amount,  order=order)

@app.route('/buy-now', methods=['POST'])
@login_required
def buy_now():
    if current_user.is_authenticated:
        cart_items = CartItem.query.all()
        # Calculate the total amount from the cart items
        total_amount = sum(item['product'].price * item['quantity'] for item in cart_items)

        # Create a new order for the authenticated user
        order = Order(user_id=current_user.id, total_amount=total_amount, status='pending')
        db.session.add(order)
        db.session.commit()
        
        # Add items from the cart to the OrderItem table
        for item in cart_items:
            order_item = OrderItem(order_id=order.id, product_id=item['product'].id, quantity=item['quantity'], price=item['product'].price)
            db.session.add(order_item)

        db.session.commit()

        # Redirect to the checkout session creation route
        return redirect(url_for('create_checkout', order_id=order.id))

    flash('Please log in to complete your purchase.')
    return redirect(url_for('cart'))

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    product = Product.query.get(product_id)
    
    if not product:
        flash('Product not found.')
        return redirect(url_for('home'))
    
    try:
        product_stocks = int(product.stocks)  # Convert to int if necessary
    except (ValueError, TypeError):
        product_stocks = 0
        
    # if not product or quantity > int(product.stocks):
    #     flash('Product is not available.')
    #     return redirect(url_for('home'))
    
    if quantity > product_stocks:
        flash('Product is not available in the requested quantity.')
        return redirect(url_for('home'))
    
    if 'cart' not in session:
        session['cart'] = {}

    product_id_str = str(product_id)

    if product_id_str in session['cart']:
        session['cart'][product_id_str] += quantity
    else:
        session['cart'][product_id_str] = quantity

    session.modified = True
    
    return redirect(url_for('cart'))


@app.route('/remove-from-cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session and product_id in session['cart']:
        del session['cart'][product_id]
        session.modified = True 
    return redirect(url_for('cart'))

@app.route('/order/confirmation/<int:order_id>')
def order_confirmation(order_id):
    order = Order.query.get(order_id)
    
    if not order or order.user_id != current_user.id:
        return redirect(url_for('home'))
    
    order_items = OrderItem.query.filter_by(order_id=order_id).all()
    total_price = sum(item.quantity * item.price for item in order_items)
    
    return render_template('order_confirmation.html', order=order, order_items=order_items, total_price=total_price)

# -------------------------------------------------------------#
# ---------------------order - history------------------------ #
# -------------------------------------------------------------#

@app.route('/create-order', methods=['POST'])
@login_required
def create_order():
    
    order = Order(user_id=current_user.id, status='pending')
    db.session.add(order)
    db.session.commit()
    
    # Add order items
    for product_id, quantity in session['cart'].items():
        order_item = OrderItem(order_id=order.id, product_id=product_id, quantity=quantity)
        db.session.add(order_item)
    
    db.session.commit()
    return redirect(url_for('order_history'))

@app.route('/order/history')
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    
    return render_template('order_history.html', orders=orders)

# -------------------------------------------------------------#
# ---------------------------Payment-------------------------- #
# -------------------------------------------------------------#


@app.route('/create-checkout-session/<int:order_id>', methods=['POST'])
def create_checkout(order_id):
    order = Order.query.get(order_id)
    if not order or order.user_id != current_user.id:
        flash('Order not found or invalid.', 'error')
        return redirect(url_for('order_history'))
    
    session_id = create_checkout_session(order_id)
    if session_id:
        return redirect(f"https://checkout.stripe.com/pay/{session_id}")
    flash('Order not found or invalid.', 'error')
    return redirect(url_for('order_history'))

@app.route('/payment-success/<int:order_id>', methods=['GET'])
def payment_success(order_id):
    session_id = request.args.get('session_id')
    if confirm_payment(session_id):
        flash('Payment successful!', 'success')
    else:
        flash('Payment failed or was canceled.', 'error')
    return redirect(url_for('order_history'))

@app.route('/payment-cancel/<int:order_id>', methods=['GET'])
def payment_cancel(order_id):
    flash('Payment was canceled.', 'warning')
    return redirect(url_for('order_history'))


# -------------------------------------------------------------#
# ------------------------Search------------------------------ #
# -------------------------------------------------------------#

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    else:
        products = Product.query.all()
    
    return render_template('search_results.html', products=products)


# -------------------------------------------------------------#
# ------------------------Admin------------------------------- #
# -------------------------------------------------------------#

@app.route('/admin')
@admin_only
def admin_dashboard():
    # if not current_user.is_admin:
    #     return redirect(url_for('home'))
    
    products = Product.query.all()
    users = User.query.all()
    orders = Order.query.all()
    
    return render_template('admin_dashboard.html', products=products, users=users, orders=orders)

@app.route('/admin/product/update/<int:product_id>', methods=['GET', 'POST'])
@admin_only
def update_product_stock(product_id):
    product = Product.query.get(product_id)
    
    # if not product or not current_user.is_admin:
    #     return redirect(url_for('home'))
    
    form = UpdateProductForm()
    if form.validate_on_submit():
        product.stock = form.stock.data
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    
    return render_template('update_product_stock.html', form=form, product=product)

@app.route('/admin/product/add', methods=['GET', 'POST'])
@admin_only
def add_product():
    form = ProductForm()
    form.category_id.choices = [(category.id, category.name) for category in Category.query.all()]

    if form.validate_on_submit():
        if form.new_category.data:
            category = Category.query.filter_by(name=form.new_category.data).first()
            if not category:
                category = Category(name=form.new_category.data)
                db.session.add(category)
                db.session.commit()
            category_id = category.id
        else:
            category_id = form.category_id.data
        
        image_file = form.image.data
        filename = secure_filename(image_file.filename)
        image_path = os.path.join('static/uploads', filename)
        image_file.save(image_path)
        
        product = Product(
            name=form.name.data,
            stocks=form.stocks.data,
            description=form.description.data,
            detail=form.detail.data,
            category_id=category_id,
            price=form.price.data,
            image_url=image_path
        )
        
        db.session.add(product)
        db.session.commit()
        flash("Product added successfully!", "success") 
        return redirect(url_for('admin_dashboard'))

    return render_template('add_product.html', form=form)

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_only  # if needed for permissions
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.stocks = form.stocks.data
        product.description = form.description.data
        product.detail = form.detail.data
        product.category_id = form.category_id.data
        product.price = form.price.data
        
        # Handle image update if necessary
        if form.image.data:
            image_file = form.image.data
            filename = secure_filename(image_file.filename)
            image_path = os.path.join('static/uploads', filename)
            image_file.save(image_path)
            product.image_url = image_path

        db.session.commit()
        return redirect(url_for('admin_dashboard'))  # or wherever you'd like to redirect
    
    return render_template('edit_product.html', form=form, product=product)

@app.route('/admin/orders')
@admin_only
def admin_orders():
    orders = Order.query.all()
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/order/update/<int:order_id>', methods=['GET', 'POST'])
@admin_only
def update_order_status(order_id):
    order = Order.query.get(order_id)
    
    if not order:
        return redirect(url_for('admin_dashboard'))
    
    form = UpdateOrderStatusForm()
    if form.validate_on_submit():
        order.status = form.status.data
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    
    order_items = OrderItem.query.filter_by(order_id=order_id).all()
    return render_template('update_order_status.html', form=form, order=order, order_items=order_items)

@app.route('/admin/product/delete/<int:product_id>', methods=['POST'])
@admin_only  # if you have permission checks
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin_dashboard')) 

if __name__ == '__main__':
    app.run(debug=True)