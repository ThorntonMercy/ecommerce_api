from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import UniqueConstraint
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/ecommerce_api'

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Database models 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    email = db.Column(db.String(100), unique=True)
    orders = db.relationship('Order', backref='user', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, default=lambda: datetime.now(datetime.timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    products = db.relationship('Product', secondary='order_product', backref='orders')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100))
    price = db.Column(db.Float)

class OrderProduct(db.Model): # Association table for many-to-many Product <-> Orders 
    __tablename__ = 'order_product'
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    __table_args__ = (UniqueConstraint('order_id', 'product_id', name='uix_order_product'),)

# Schemas
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True
        load_instance = True

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True

user_schema = UserSchema()
users_schema = UserSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# User Endpoints [adding, accessing, updating, deleting users]
@app.route('/users', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)  # pagination
    per_page = request.args.get('per_page', 10, type=int)
    paginated_users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    return users_schema.jsonify(paginated_users.items)

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    return user_schema.jsonify(User.query.get_or_404(id))

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(**data)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user), 201

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get_or_404(id)
    for key, value in request.json.items():
        setattr(user, key, value)
    db.session.commit()
    return user_schema.jsonify(user)

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

# Product Endpoints [adding, accessing, updating, deleting products]
@app.route('/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)  # pagination
    per_page = request.args.get('per_page', 10, type=int)
    paginated_products = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    return products_schema.jsonify(paginated_products.items)

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    return product_schema.jsonify(Product.query.get_or_404(id))

@app.route('/products', methods=['POST'])
def create_product():
    data = request.json
    new_product = Product(**data)
    db.session.add(new_product)
    db.session.commit()
    return product_schema.jsonify(new_product), 201

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    for key, value in request.json.items():
        setattr(product, key, value)
    db.session.commit()
    return product_schema.jsonify(product)

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return '', 204

# Order Endpoints [adding, accessing, updating, deleting orders and managing products in orders]
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    new_order = Order(user_id=data['user_id'], order_date=datetime.strptime(data['order_date'], '%Y-%m-%d'))
    db.session.add(new_order)
    db.session.commit()
    return order_schema.jsonify(new_order), 201

@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product_to_order(order_id, product_id):
    if OrderProduct.query.filter_by(order_id=order_id, product_id=product_id).first():
        return jsonify({'message': 'Product is already in your order, yay!'}), 400 #ensures no duplicates 
    db.session.add(OrderProduct(order_id=order_id, product_id=product_id))
    db.session.commit()
    return jsonify({'message': 'Product added, yay!'})

@app.route('/orders/<int:order_id>/remove_product', methods=['DELETE'])
def remove_product_from_order(order_id):
    data = request.json
    product_id = data.get('product_id')
    association = OrderProduct.query.filter_by(order_id=order_id, product_id=product_id).first_or_404()
    db.session.delete(association)
    db.session.commit()
    return jsonify({'message': 'Product removed successfully!'})

@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_orders_by_user(user_id):
    orders = Order.query.filter_by(user_id=user_id).all()
    return orders_schema.jsonify(orders)

@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_products_for_order(order_id):
    order = Order.query.get_or_404(order_id)
    return products_schema.jsonify(order.products)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
