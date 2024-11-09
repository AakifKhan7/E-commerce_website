from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, IntegerField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

class SignUp(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    name = StringField("Name", validators=[DataRequired(), Length(max=30)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=15)])
    
    street = StringField("Street Address", validators=[DataRequired(), Length(max=100)])
    city = StringField("City", validators=[DataRequired(), Length(max=50)])
    state = StringField('state', validators=[DataRequired(), Length(max=20)])
    postal_code = StringField("Postal Code", validators=[DataRequired(), Length(max=20)])
    country = StringField("Country", validators=[DataRequired(), Length(max=50)])
    phone_number = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=15)])

    submit = SubmitField("Sign Me Up!")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")
    
# only for admin
class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    stocks = IntegerField('Stock Quantity', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    detail = TextAreaField('Detail', validators=[DataRequired()])
    category_id = SelectField("Category", coerce=int, validators=[Optional()])
    new_category = StringField("New Category", validators=[Optional(), Length(max=100)])
    price = IntegerField('Price', validators=[DataRequired()])
    image = FileField('Product Image')
    
    
    submit = SubmitField('Submit')
    
class ProductOrderForm(FlaskForm):
    product_id = SelectField("Select Product", coerce=int, validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Place Order")

class PaymentForm(FlaskForm):
    card_number = StringField("Card Number", validators=[DataRequired(), Length(min=16, max=16)])
    expiration_date = StringField("Expiration Date (MM/YY)", validators=[DataRequired(), Length(min=5, max=5)])
    cvv = StringField("CVV", validators=[DataRequired(), Length(min=3, max=3)])
    billing_address = StringField("Billing Address", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Pay Now")

class OrderConfirmationForm(FlaskForm):
    order_id = IntegerField("Order ID", validators=[DataRequired()])
    shipping_address = StringField("Shipping Address", validators=[DataRequired()])
    total_amount = FloatField("Total Amount", validators=[DataRequired()])
    submit = SubmitField("Confirm Order")

class UpdateProductForm(FlaskForm):
    stocks = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Stock')
    

class UpdateOrderStatusForm(FlaskForm):
    status = SelectField("Order Status", choices=[
        ("pending", "pending"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled")
    ], validators=[DataRequired()])
    submit = SubmitField("Update Status")
