from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

STOCK = {"apple": 50, "banana": 0, "laptop": 3}

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/inventory")
def inventory():
    request_id = request.headers.get("X-Request-Id", "no-id")
    item = request.args.get("item", "")
    logging.info(f"method=GET path=/inventory request_id={request_id} item={item}")
    if item not in STOCK:
        return jsonify({"error": f"item '{item}' unknown"}), 404
    if STOCK[item] == 0:
        return jsonify({"item": item, "in_stock": False, "quantity": 0}), 200
    return jsonify({"item": item, "in_stock": True, "quantity": STOCK[item]}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)