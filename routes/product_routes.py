from flask import Blueprint, request, jsonify, render_template, redirect
from models.sql_models import Product, db

def create_product_bp(mongo):
    product_bp = Blueprint('product_bp', __name__)

    @product_bp.route('/add_review', methods=['POST'])
    def add_review():
        data = request.json
        mongo.db.reviews.insert_one({
            "product_id": int(data['product_id']),
            "user": data['user'],
            "rating": data['rating'],
            "comment": data['comment']
        })
        return jsonify({"msg": "Review added"}), 201

    @product_bp.route('/reviews/<int:product_id>', methods=['GET'])
    def get_reviews(product_id):
        reviews = mongo.db.reviews.find({"product_id": product_id}, {"_id": 0})
        return jsonify([{
            "user": r["user"],
            "rating": r["rating"],
            "comment": r["comment"]
        } for r in reviews])

    @product_bp.route('/')
    def home():
        products = Product.query.all()
        reviews = mongo.db.reviews.find({}, {"_id": 0})
        return render_template("index.html", products=products, reviews=reviews)

    @product_bp.route('/products')
    def list_products():
        products = Product.query.all()
        return render_template('products.html', products=products)
    


    @product_bp.route('/products/add', methods=['GET', 'POST'])
    def add_product():
        if request.method == 'POST':
            new_product = Product(
                name=request.form['name'],
                brand=request.form['brand'],
                category=request.form['category'],
                price=float(request.form['price']),
                stock_level=int(request.form['stock'])
            )
            db.session.add(new_product)
            db.session.commit()
            return redirect('/products')
        return render_template('add_product.html')  # <-- moved outside the POST block

    @product_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
    def edit_product(product_id):
        product = Product.query.get_or_404(product_id)
        if request.method == 'POST':
            product.name = request.form['name']
            product.brand = request.form['brand']
            product.category = request.form['category']
            product.price = float(request.form['price'])
            product.stock_level = int(request.form['stock'])
            db.session.commit()
            return redirect('/products')
        return render_template('edit_product.html', product=product)

    @product_bp.route('/products/delete/<int:product_id>')
    def delete_product(product_id):
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return redirect('/products')





    return product_bp




