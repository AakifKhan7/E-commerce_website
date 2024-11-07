import stripe
from flask import current_app, redirect, url_for, flash
from model import Order, OrderItem
from database import db

stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

def create_checkout_session(order_id):
    order = Order.query.get(order_id)
    
    if not order:
        return None
    
    line_items = [
        {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.product.name,
                },
                'unit_amount': int(item.product.price * 100),
            },
            'quantity': item.quantity,
        }
        for item in OrderItem.query.filter_by(order_id=order_id).all()
    ]
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=url_for('payment_success', order_id=order_id, _external=True),
        cancel_url=url_for('payment_cancel', order_id=order_id, _external=True),
        client_reference_id=order_id,
    )
    
    return session.id

def confirm_payment(session_id):
    session = stripe.checkout.Session.retrieve(session_id)
    
    if session.payment_status == 'paid':
        order = Order.query.get(session.client_reference_id)
        order.status = 'paid'
        db.session.commit()
        return True
    
    return False
