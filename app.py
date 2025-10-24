from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

orders = []
PRODUCT_SERVICE_URL = "http://product_service:5001/products"

# GET all orders
@app.route("/orders", methods=["GET"])
def get_orders():
    return jsonify(orders)

# POST - create order
@app.route("/orders/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get("status")
    if new_status not in ["Pending", "Completed", "Cancelled"]:
        return jsonify({"error": "Invalid status"}), 400

    order = next((o for o in orders if o["order_id"] == order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    order["status"] = new_status
    return jsonify(order)
@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id or quantity <= 0:
        return jsonify({"error": "Invalid order data"}), 400

    # Fetch product info from product service
    try:
        res = requests.get(f"{PRODUCT_SERVICE_URL}/{product_id}")
        res.raise_for_status()
        product = res.json()
    except Exception as e:
        return jsonify({"error": "Product not found"}), 404

    order_id = len(orders) + 1
    order = {
        "order_id": order_id,
        "product_id": product_id,
        "quantity": quantity,
        "product": product,
        "status": "Pending"  # default status
    }
    orders.append(order)
    return jsonify(order), 201

# DELETE order
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    global orders
    orders = [o for o in orders if o["order_id"] != order_id]
    return jsonify({"message": "Order deleted"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
