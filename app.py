# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DB_FILE = "bakecart.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        quantity INTEGER,
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)
    conn.commit()
    conn.close()

init_db()

# GET all orders
@app.route("/orders", methods=["GET"])
def get_orders():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT o.order_id, o.quantity, o.status, p.id, p.name, p.price
    FROM orders o
    JOIN products p ON o.product_id = p.id
    """)
    orders = []
    for row in cursor.fetchall():
        orders.append({
            "order_id": row[0],
            "quantity": row[1],
            "status": row[2],
            "product": {"id": row[3], "name": row[4], "price": row[5]}
        })
    conn.close()
    return jsonify(orders)

# POST create order
@app.route("/orders", methods=["POST"])
def add_order():
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (product_id, quantity) VALUES (?, ?)", (product_id, quantity))
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return jsonify({"order_id": order_id, "product_id": product_id, "quantity": quantity, "status": "Pending"}), 201

# PUT update status
@app.route("/orders/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    data = request.get_json()
    status = data.get("status")
    if status not in ["Pending", "Completed", "Cancelled"]:
        return jsonify({"error": "Invalid status"}), 400
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status=? WHERE order_id=?", (status, order_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Status updated"}), 200

# DELETE order
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE order_id=?", (order_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Order deleted"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
