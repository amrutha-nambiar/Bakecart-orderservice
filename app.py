import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

PRODUCT_SERVICE_URL = "http://product_service:5001/products"
ORDERS_FILE = "orders.json"

# Load orders from file
try:
    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)
except:
    orders = []

# Save orders to file
def save_orders():
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f)

# GET all orders
@app.route("/orders", methods=["GET"])
def get_orders():
    return jsonify(orders)

# POST create order
@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or not quantity:
        return jsonify({"error": "Missing product_id or quantity"}), 400

    # Fetch product info from product service
    r = requests.get(f"{PRODUCT_SERVICE_URL}/{product_id}")
    if r.status_code != 200:
        return jsonify({"error": "Product not found"}), 404
    product = r.json()

    order_id = max([o["order_id"] for o in orders], default=0) + 1
    order = {
        "order_id": order_id,
        "product": product,
        "quantity": quantity,
        "status": "Pending"
    }
    orders.append(order)
    save_orders()
    return jsonify(order), 201

# PUT update status
@app.route("/orders/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get("status")
    if new_status not in ["Pending","Completed","Cancelled"]:
        return jsonify({"error": "Invalid status"}), 400
    order = next((o for o in orders if o["order_id"]==order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    order["status"] = new_status
    save_orders()
    return jsonify(order)

# DELETE order
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    global orders
    orders = [o for o in orders if o["order_id"] != order_id]
    save_orders()
    return jsonify({"message": "Order deleted"}), 200

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5002)
