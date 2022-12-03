from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
cors = CORS(app, resources={r"/*":{"origins":"*"}})

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), unique=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password
        
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'password')

user_schema = UserSchema()


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False)
    desc = db.Column(db.String(500), unique=False)
    category = db.Column(db.String(200), unique=False)
    price = db.Column(db.Integer, unique=False)
    url = db.Column(db.String(200), unique=False)

    def __init__(self, name, desc, category, price, url):
        self.name = name
        self.desc = desc
        self.category = category
        self.price = price
        self.url = url


class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'desc', 'category', 'price', 'url')


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


# Endpoint to Add a User
@app.route('/user', methods=['POST'])
def add_user():
    email = request.json['email']
    password = request.json['password']

    user_check = db.session.query(User).filter(User.email == email).first()

    if user_check is not None:
        return jsonify('Please choose a different email')

    new_user = User(email, password)

    db.session.add(new_user)
    db.session.commit()

    result = user_schema.dump(new_user)

    return jsonify({'user': result})

# Endpoint to login user
@app.route('/login', methods=['POST'])
def login_user():
    email = request.json['email']
    password = request.json['password']

    user = db.session.query(User).filter(User.email == email).first()

    if user == None:
        return jsonify('User does not exist')
    
    if user.password != password:
        return jsonify('Wrong password')

    return jsonify({'LOGGED_IN': True})

# Endpoint to Create a New Product
@app.route('/product', methods=['POST'])
def add_product():
    # 'name', 'desc', 'category', 'price'
    name = request.json['name']
    desc = request.json['desc']
    category = request.json['category']
    price = request.json['price']
    url = request.json['url']

    
    new_product = Product(name, desc, category, price, url)

    db.session.add(new_product)
    db.session.commit()

    product = Product.query.get(new_product.id)
    return product_schema.jsonify(product), 201

# Endpoint to query all products
@app.route('/products', methods=['GET'])
def get_products():
    all_products = Product.query.all()
    result = products_schema.dump(all_products)
    return jsonify(result), 200

# Endpoint to query one product
@app.route('/product/<id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    return product_schema.jsonify(product), 200

# Endpoint to update a product
@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    name = request.json['name']
    desc = request.json['desc']
    category = request.json['category']
    price = request.json['price']
    url = request.json['url']

    product.name = name if name else product.name
    product.desc = desc if desc else product.desc
    product.category = category if category else product.category
    product.price = price if price else product.price
    product.url = url if url else product.url

    db.session.commit()
    return product_schema.jsonify(product), 200

# Endpoint to delete a product
@app.route('/product/<id>', methods=['DELETE'])
def delete_post(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()

    return jsonify({'msg': 'Product was successfully deleted!'}), 200


if __name__ == '__main__':
    app.run(debug=True)