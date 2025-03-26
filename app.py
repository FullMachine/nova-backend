from flask import Flask, jsonify, request
app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return 'Nova Backend is live!'

# Test route
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'Nova says pong!'}), 200
