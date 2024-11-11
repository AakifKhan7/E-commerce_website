from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, DateTime
from flask_login import UserMixin
from datetime import datetime
from database import db



class Category(db.Model):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    products = relationship('Product', back_populates='category')

class Product(db.Model):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    stocks: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    detail: Mapped[str] = mapped_column(String(250), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('categories.id'))
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    image_url: Mapped[str] = mapped_column(String(250), nullable=True) 

    category = relationship('Category', back_populates='products')
    order_items = relationship('OrderItem', back_populates='product')
    cart_items = relationship('CartItem', back_populates='product')

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    
    street: Mapped[str] = mapped_column(String(250))
    city: Mapped[str] = mapped_column(String(15))
    state: Mapped[str] = mapped_column(String(10))
    postal_code: Mapped[str] = mapped_column(String(15))
    country: Mapped[str] = mapped_column(String(15))
    phone_number: Mapped[str] = mapped_column(String(20))

    cart = relationship("Cart", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user")

class Cart(db.Model):
    __tablename__ = 'carts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('users.id'))
    
    user = relationship('User', back_populates='cart')
    items = relationship('CartItem', back_populates='cart')

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    total_amount: Mapped[int] = mapped_column(Integer, db.ForeignKey('carts.id'))
    product_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('products.id'))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    cart = relationship('Cart', back_populates='items')
    product = relationship('Product', back_populates='cart_items')

class Order(db.Model):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('users.id'))
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable='False')
    
    user = relationship('User', back_populates='orders')
    items = relationship('OrderItem', back_populates='order')
    payment = relationship('Payment', uselist=False, back_populates='order')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('orders.id'))
    product_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('products.id'))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='order_items')

class Payment(db.Model):
    __tablename__ = 'payments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('orders.id'))
    payment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'Completed', 'Pending'
    
    order = relationship('Order', back_populates='payment')
