import stripe
from flask import current_app, redirect, url_for, flash
from model import Order, OrderItem  # Make sure your model file is correctly imported
from database import db  # Ensure you're importing the correct db session
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv('STRIPE_API_KEY')
print(os.getenv('STRIPE_API_KEY'))

def create_checkout_session(order_id):
    order = Order.query.get(order_id)
    
    if not order:
        flash("Order not found.", "danger")
        return None
    
    line_items = []
    for item in order.items:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.product.name,
                },
                'unit_amount': int(item.product.price * 100),
            },
            'quantity': item.quantity,
        })
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('payment_success', order_id=order_id, _external=True, _scheme='http') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('payment_cancel', order_id=order_id, _external=True, _scheme='http') + '?session_id={CHECKOUT_SESSION_ID}',
            client_reference_id=order_id,
        )
        print(f"Created session ID: {session.id}")
        return session.url  # Return the session URL directly for redirect
    
    except stripe.error.StripeError as e:
        flash(f"Stripe error: {str(e)}", "danger")
        return None

def confirm_payment(session_id):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            order = Order.query.get(session.client_reference_id)
            order.status = 'paid'
            db.session.commit()
            return True
        
    except stripe.error.StripeError as e:
        flash(f"Stripe error: {str(e)}", "danger")
    
    return False
