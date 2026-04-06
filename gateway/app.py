from flask import Flask, request, jsonify
import logging, uuid, requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def get_request_id():
    return request.headers.get("X-Request-Id", str(uuid.uuid4()))

@app.before_request
def log_request():
    rid = get_request_id()
    logging.info(f"method={request.method} path={request.path} request_id={rid}")

@app.route("/")
def ui():
    return "<h1>Checkout System</h1>"

@app.route("/api/arch")
def arch():
    return "gateway->checkout->pricing+inventory->postgres", 200

@app.route("/api/ping")
def ping():
    return jsonify({"status": "pong"}), 200

@app.route("/api/checkout", methods=["POST"])
def checkout():
    request_id = get_request_id()

    try:
        response = requests.post(
            "http://checkout/api/checkout",
            json=request.json,
            headers={"X-Request-Id": request_id},
            timeout=3
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException:
        return jsonify({"error": "checkout unavailable"}), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)