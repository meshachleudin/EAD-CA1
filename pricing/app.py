from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

PRICES = {"apple": 1.2, "banana": 0.5, "laptop": 999}

@app.route("/price")
def price():
    request_id = request.headers.get("X-Request-Id", "no-id")
    item = request.args.get("item", "")

    logging.info(f"method=GET path=/price request_id={request_id} item={item}")

    if item not in PRICES:
        return jsonify({"error": "not found"}), 404

    return jsonify({"price": PRICES[item]}), 200

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

# 🔥 THIS WAS MISSING
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)