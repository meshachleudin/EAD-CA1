from flask import Flask, request, jsonify
import requests, logging, os, psycopg2

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

PRICING_URL  = os.getenv("PRICING_URL",  "http://pricing")
INVENTORY_URL = os.getenv("INVENTORY_URL", "http://inventory")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PASS = os.getenv("DB_PASS", "")

def get_db():
    return psycopg2.connect(
        host=DB_HOST, dbname="checkoutdb",
        user="checkoutuser", password=DB_PASS
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

    headers = {"X-Request-Id": request_id}  # Propagate to downstream services

    # Call pricing with timeout
    try:
        price_resp = requests.get(f"{PRICING_URL}/price", params={"item": item},
                                  headers=headers, timeout=3)
        price_data = price_resp.json()
        if price_resp.status_code != 200:
            return jsonify({"error": "pricing failed", "detail": price_data}), 502
    except requests.Timeout:
        logging.error(f"request_id={request_id} pricing timeout")
        return jsonify({"error": "pricing service timed out"}), 504
    except Exception as e:
        logging.error(f"request_id={request_id} pricing error: {e}")
        return jsonify({"error": "pricing unavailable"}), 503

    # Call inventory with timeout
    try:
        inv_resp = requests.get(f"{INVENTORY_URL}/inventory", params={"item": item},
                                headers=headers, timeout=3)
        inv_data = inv_resp.json()
        if not inv_data.get("in_stock"):
            return jsonify({"error": "out of stock", "item": item}), 409
    except requests.Timeout:
        logging.error(f"request_id={request_id} inventory timeout")
        return jsonify({"error": "inventory service timed out"}), 504
    except Exception as e:
        logging.error(f"request_id={request_id} inventory error: {e}")
        return jsonify({"error": "inventory unavailable"}), 503

    # Write to Postgres
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS orders (id SERIAL PRIMARY KEY, item TEXT, price FLOAT, request_id TEXT)")
        cur.execute("INSERT INTO orders (item, price, request_id) VALUES (%s, %s, %s)",
                    (item, price_data["price"], request_id))
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        logging.warning(f"request_id={request_id} db write failed: {e}")

    return jsonify({"status": "ok", "item": item, "price": price_data["price"], "request_id": request_id}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)