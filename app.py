# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
CORS(app, origins=["https://amrutha-nambiar.github.io/Bakecart-frontend/"])


# Connect to PostgreSQL on Render
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')  # Render sets this
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="Pending")
    product = db.relationship('Product')

# Create tables
with app.app_context():
    db.create_all()

# GET all orders
@app.route("/orders", methods=["GET"])
def get_orders():
    orders = Order.query.all()
    result = []
    for o in orders:
        result.append({
            "order_id": o.order_id,
            "quantity": o.quantity,
            "status": o.status,
            "product": {"id": o.product.id, "name": o.product.name, "price": o.product.price} if o.product else None
        })
    return jsonify(result)

# POST create order
@app.route("/orders", methods=["POST"])
def add_order():
    data = request.get_json()
    order = Order(product_id=data.get("product_id"), quantity=data.get("quantity"))
    db.session.add(order)
    db.session.commit()
    return jsonify({"order_id": order.order_id, "product_id": order.product_id, "quantity": order.quantity, "status": order.status}), 201

# PUT update status
@app.route("/orders/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    data = request.get_json()
    status = data.get("status")
    if status not in ["Pending", "Completed", "Cancelled"]:
        return jsonify({"error": "Invalid status"}), 400
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    order.status = status
    db.session.commit()
    return jsonify({"message": "Status updated"}), 200

# DELETE order
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order deleted"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5002)))

