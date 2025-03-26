from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "Nova Backend is live!"

# ------------------ NBA Stats (BallDontLie) ------------------
@app.route('/nba/player_stats', methods=['GET'])
def nba_player_stats():
    player_name = request.args.get('player')
    if not player_name:
        return jsonify({'error': 'Missing player name'}), 400

    try:
        url = f"https://www.balldontlie.io/api/v1/players?search={player_name}"
        response = requests.get(url)
        data = response.json()

        if not data['data']:
            return jsonify({'error': 'Player not found'}), 404

        player_id = data['data'][0]['id']
        stats_url = f"https://www.balldontlie.io/api/v1/season_averages?player_ids[]={player_id}"
        stats_response = requests.get(stats_url)
        stats = stats_response.json()

        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------ Soccer Stats (API-FOOTBALL via RapidAPI) ------------------
@app.route('/soccer/player_stats', methods=['GET'])
def soccer_stats():
    player_name = request.args.get('player')
    if not player_name:
        return jsonify({'error': 'Missing player name'}), 400

    headers = {
        'X-RapidAPI-Key': os.environ.get('API_FOOTBALL_KEY'),
        'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com'
    }

    url = f"https://api-football-v1.p.rapidapi.com/v3/players?search={player_name}&season=2023"

    try:
        response = requests.get(url, headers=headers)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------ New: Soccer Fixtures (Football-Data.org) ------------------
@app.route('/soccer/fixtures', methods=['GET'])
def soccer_fixtures():
    headers = {'X-Auth-Token': os.environ.get('FOOTBALL_DATA_KEY')}
    url = "https://api.football-data.org/v4/matches"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': 'Failed to fetch fixtures from Football-Data.org'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------ Esports Stats (PandaScore) ------------------
@app.route('/esports/player_stats', methods=['GET'])
def esports_stats():
    player_name = request.args.get('player')
    if not player_name:
        return jsonify({'error': 'Missing player name'}), 400

    headers = {
        'Authorization': f"Bearer {os.environ.get('PANDASCORE_API_KEY')}"
    }

    url = f"https://api.pandascore.co/players?search[name]={player_name}"

    try:
        response = requests.get(url, headers=headers)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------ Betting Odds (OddsAPI) ------------------
@app.route('/odds', methods=['GET'])
def odds():
    sport = request.args.get('sport', 'basketball_nba')
    region = request.args.get('region', 'us')
    market = request.args.get('market', 'h2h')

    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        'apiKey': os.environ.get('ODDS_API_KEY'),
        'regions': region,
        'markets': market,
        'oddsFormat': 'decimal'
    }

    try:
        response = requests.get(url, params=params)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------ Error Handling ------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Route not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
