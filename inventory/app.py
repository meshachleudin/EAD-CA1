from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

STOCK = {"apple": 50, "banana": 0, "laptop": 3}

@app.route("/inventory")
def inventory():
    request_id = request.headers.get("X-Request-Id", "no-id")
    item = request.args.get("item", "")

    logging.info(f"method=GET path=/inventory request_id={request_id} item={item}")

    if item not in STOCK:
        return jsonify({"error": "unknown item"}), 404

    return jsonify({
        "item": item,
        "in_stock": STOCK[item] > 0,
        "quantity": STOCK[item]
    }), 200

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

# 🔥 THIS WAS MISSING
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)