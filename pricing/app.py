from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

PRICES = {"apple": 1.20, "banana": 0.50, "laptop": 999.00}

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/price")
def price():
    request_id = request.headers.get("X-Request-Id", "no-id")
    item = request.args.get("item", "")
    logging.info(f"method=GET path=/price request_id={request_id} item={item}")
    if item not in PRICES:
        return jsonify({"error": f"item '{item}' not found"}), 404
    return jsonify({"item": item, "price": PRICES[item]}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)