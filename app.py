from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "Nova Backend is live!"

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'Nova says pong!'}), 200

# ------------------ NBA Stats Endpoint (BallDontLie) ------------------
@app.route('/nba/player_stats', methods=['GET'])
def nba_player_stats():
    player_name = request.args.get('player')
    if not player_name:
        return jsonify({'error': 'Missing player name'}), 400
    try:
        # Search for the player using BallDontLie API
        search_url = f"https://www.balldontlie.io/api/v1/players?search={player_name}"
        search_response = requests.get(search_url)
        try:
            search_data = search_response.json()
        except Exception as e:
            return jsonify({
                'error': 'Error parsing JSON from players endpoint',
                'raw_response': search_response.text
            }), 500

        if not search_data.get('data'):
            return jsonify({'error': 'Player not found'}), 404

        player_id = search_data['data'][0]['id']
        # Fetch season averages for that player
        stats_url = f"https://www.balldontlie.io/api/v1/season_averages?player_ids[]={player_id}"
        stats_response = requests.get(stats_url)
        try:
            stats = stats_response.json()
        except Exception as e:
            return jsonify({
                'error': 'Error parsing JSON from season averages endpoint',
                'raw_response': stats_response.text
            }), 500

        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------ Soccer Stats Endpoint (API-Football via RapidAPI) ------------------
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
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------ Soccer Fixtures Endpoint (API-Football) ------------------
@app.route('/soccer/fixtures_apifootball', methods=['GET'])
def soccer_fixtures_apifootball():
    """
    Fetch fixtures using API-Football.
    Usage example:
      /soccer/fixtures_apifootball?league=39&season=2023
    """
    league = request.args.get('league')
    season = request.args.get('season')
    if not league or not season:
        return jsonify({'error': 'Missing league or season param. Example: ?league=39&season=2023'}), 400

    headers = {
        "X-RapidAPI-Key": os.environ.get("API_FOOTBALL_KEY"),
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?league={league}&season={season}"
    try:
        response = requests.get(url, headers=headers)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------ Soccer Fixtures Endpoint (Football-Data.org) ------------------
@app.route('/soccer/fixtures_footballdata', methods=['GET'])
def soccer_fixtures_footballdata():
    """
    Fetch fixtures using Football-Data.org.
    Usage example:
      /soccer/fixtures_footballdata?competition=2021
    (e.g., competition=2021 for EPL)
    """
    competition = request.args.get('competition', '2021')
    headers = {
        'X-Auth-Token': os.environ.get('FOOTBALL_DATA_KEY')
    }
    url = f"https://api.football-data.org/v4/competitions/{competition}/matches"
    try:
        response = requests.get(url, headers=headers)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------ Esports Stats Endpoint (PandaScore) ------------------
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
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------ Betting Odds Endpoint (OddsAPI) ------------------
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
        return jsonify(response.json()), response.status_code
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
    app.run(host='0.0.0.0', port=8080, debug=True)
