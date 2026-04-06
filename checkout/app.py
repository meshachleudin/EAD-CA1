from flask import Flask, request, jsonify
import requests, logging, os, psycopg2

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

PRICING_URL  = os.getenv("PRICING_URL", "http://pricing")
INVENTORY_URL = os.getenv("INVENTORY_URL", "http://inventory")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PASS = os.getenv("DB_PASS", "")

def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        dbname="checkoutdb",
        user="postgres",
        password=DB_PASS
    )

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/api/checkout", methods=["POST"])
def checkout():
    request_id = request.headers.get("X-Request-Id", "no-id")
    body = request.get_json(silent=True) or {}
    item = body.get("item", "")

    logging.info(f"method=POST path=/api/checkout request_id={request_id} item={item}")

    headers = {"X-Request-Id": request_id}

    # Pricing call
    try:
        price_resp = requests.get(
            f"{PRICING_URL}/price",
            params={"item": item},
            headers=headers,
            timeout=3
        )
        if price_resp.status_code != 200:
            return jsonify({"error": "pricing failed"}), 502
        price_data = price_resp.json()
    except requests.Timeout:
        return jsonify({"error": "pricing timeout"}), 504
    except Exception:
        return jsonify({"error": "pricing unavailable"}), 503

    # Inventory call
    try:
        inv_resp = requests.get(
            f"{INVENTORY_URL}/inventory",
            params={"item": item},
            headers=headers,
            timeout=3
        )
        inv_data = inv_resp.json()

        if not inv_data.get("in_stock"):
            return jsonify({"error": "out of stock"}), 409
    except requests.Timeout:
        return jsonify({"error": "inventory timeout"}), 504
    except Exception:
        return jsonify({"error": "inventory unavailable"}), 503

    # DB write
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                item TEXT,
                request_id TEXT
            )
        """)
        cur.execute(
            "INSERT INTO orders (item, request_id) VALUES (%s, %s)",
            (item, request_id)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logging.warning(f"request_id={request_id} db error={e}")

    return jsonify({
        "status": "ok",
        "item": item,
        "price": price_data["price"],
        "request_id": request_id
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)