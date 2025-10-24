from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

orders = []
next_order_id = 1
PRODUCT_SERVICE_URL = "https://bakecart-product-service.onrender.com/products"

# GET all orders
@app.route("/orders", methods=["GET"])
def get_orders():
    return jsonify(orders)

# POST - create new order
@app.route("/orders", methods=["POST"])
def create_order():
    global next_order_id
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or not quantity:
        return jsonify({"error": "Missing product_id or quantity"}), 400

    # fetch product info from product service
    try:
        res = requests.get(PRODUCT_SERVICE_URL)
        res.raise_for_status()
        products = res.json()
        product = next((p for p in products if p['id'] == product_id), None)
        if not product:
            return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    order = {
        "order_id": next_order_id,
        "product": product,
        "quantity": quantity,
        "status": "Pending"
    }
    orders.append(order)
    next_order_id += 1
    return jsonify(order), 201

# PUT - update status
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

# DELETE
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    global orders
    orders = [o for o in orders if o["order_id"] != order_id]
    return jsonify({"message": "Order deleted"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
