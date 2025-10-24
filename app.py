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
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

# GET all products
@app.route("/products", methods=["GET"])
def get_products():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM products")
    products = [{"id": row[0], "name": row[1], "price": row[2]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(products)

# POST add product
@app.route("/products", methods=["POST"])
def add_product():
    data = request.get_json()
    name = data.get("name")
    price = data.get("price")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": product_id, "name": name, "price": price}), 201

# DELETE product
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Product deleted"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
