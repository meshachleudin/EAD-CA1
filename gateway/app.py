from flask import Flask, request, jsonify
import logging, uuid, requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def get_request_id():
    return request.headers.get("X-Request-Id", str(uuid.uuid4()))

@app.route("/")
def ui():
    return "<h1>Checkout System</h1><p>POST /api/checkout to place an order.</p>", 200

@app.route("/api/arch")
def arch():
    request_id = get_request_id()
    logging.info(f"method=GET path=/api/arch request_id={request_id}")
    return "gateway->checkout->pricing+inventory->postgres", 200

@app.route("/api/ping")
def ping():
    request_id = get_request_id()
    logging.info(f"method=GET path=/api/ping request_id={request_id}")
    return jsonify({"status": "pong"}), 200

@app.route("/api/checkout", methods=["POST"])
def checkout():
    request_id = get_request_id()
    logging.info(f"method=POST path=/api/checkout request_id={request_id}")

    try:
        response = requests.post(
            "http://checkout/api/checkout",
            json=request.json,
            headers={"X-Request-Id": request_id},
            timeout=3
        )
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        logging.error(f"request_id={request_id} error={str(e)}")
        return jsonify({"error": "checkout unavailable"}), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)