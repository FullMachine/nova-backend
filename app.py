from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

@app.route('/')
def home():
    return 'Nova Backend is live!'

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'Nova says pong!'}), 200

@app.route('/odds/nba', methods=['GET'])
def get_nba_odds():
    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"
    params = {
        'apiKey': os.getenv("ODDS_API_KEY"),
        'regions': 'us',
        'markets': 'h2h,spreads,totals',
        'oddsFormat': 'decimal'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"error": "Failed to fetch NBA odds"}), 500

@app.route('/soccer/matches', methods=['GET'])
def get_football_matches():
    headers = {'X-Auth-Token': os.getenv('FOOTBALL_DATA_API_KEY')}
    url = "https://api.football-data.org/v4/matches"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({'error': 'Failed to fetch football data'}), 500

@app.route('/api-football/live', methods=['GET'])
def get_api_football_live():
    headers = {
        "X-RapidAPI-Key": os.getenv("RAPID_API_FOOTBALL_KEY"),
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({'error': 'Failed to fetch API-FOOTBALL live data'}), 500

@app.route('/pandascore/matches', methods=['GET'])
def get_pandascore_matches():
    url = "https://api.pandascore.co/matches/upcoming"
    headers = {"Authorization": f"Bearer {os.getenv('PANDASCORE_API_KEY')}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({'error': 'Failed to fetch PandaScore data'}), 500

if __name__ == '__main__':
    app.run(debug=True)
