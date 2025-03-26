from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Nova Backend is live!"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    return jsonify({"message": "Received data", "data": data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
