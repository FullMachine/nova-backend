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

# ------------------ NBA Stats (BallDontLie) ------------------
# Official docs: https://www.balldontlie.io/#introduction
# Requires ?player= (e.g. "lebron james") and ?season= (e.g. "2022")
@app.route('/nba/player_stats', methods=['GET'])
def nba_player_stats():
    player_name = request.args.get('player')  # e.g. "lebron james"
    season = request.args.get('season')       # e.g. "2022"
    if not player_name or not season:
        return jsonify({
            'error': 'Missing params. Usage: /nba/player_stats?player=lebron james&season=2022'
        }), 400

    try:
        # 1) Search for the player on "www.balldontlie.io/api/v1" using a user-agent
        search_url = f"https://www.balldontlie.io/api/v1/players?search={player_name}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        search_resp = requests.get(search_url, headers=headers)

        # Attempt to parse JSON
        try:
            search_data = search_resp.json()
        except:
            return jsonify({
                'error': 'Error parsing JSON from BallDontLie search',
                'raw_response': search_resp.text[:500]
            }), 500

        if not search_data.get('data'):
            return jsonify({'error': 'Player not found'}), 404

        # Grab the first matching player
        player_id = search_data['data'][0]['id']

        # 2) Fetch season averages
        stats_url = f"https://www.balldontlie.io/api/v1/season_averages?season={season}&player_ids[]={player_id}"
        stats_resp = requests.get(stats_url, headers=headers)
        try:
            stats_data = stats_resp.json()
        except:
            return jsonify({
                'error': 'Error parsing JSON from BallDontLie season averages',
                'raw_response': stats_resp.text[:500]
            }), 500

        return jsonify(stats_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------ Soccer Player Stats (API-Football) ------------------
# Official docs: https://www.api-football.com/documentation-v3
# Typically requires ?player=, ?league=, ?season=
@app.route('/soccer/player_stats', methods=['GET'])
def soccer_player_stats():
    player_name = request.args.get('player')
    league = request.args.get('league')
    season = request.args.get('season')
    if not player_name or not league or not season:
        return jsonify({
            'error': 'Missing params. Usage: /soccer/player_stats?player=haaland&league=39&season=2023'
        }), 400

    headers = {
        'X-RapidAPI-Key': os.environ.get('API_FOOTBALL_KEY'),
        'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com'
    }
    url = f"https://api-football-v1.p.rapidapi.com/v3/players?search={player_name}&league={league}&season={season}"
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if not data.get('response'):
            return jsonify({'error': 'Player not found or no data'}), 404
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------ Soccer Fixtures (API-Football) ------------------
@app.route('/soccer/fixtures_apifootball', methods=['GET'])
def soccer_fixtures_apifootball():
    """
    Usage: /soccer/fixtures_apifootball?league=39&season=2023
    """
    league = request.args.get('league')
    season = request.args.get('season')
    if not league or not season:
        return jsonify({'error': 'Missing league or season. e.g. ?league=39&season=2023'}), 400

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

# ------------------ Soccer Fixtures (Football-Data.org) ------------------
@app.route('/soccer/fixtures_footballdata', methods=['GET'])
def soccer_fixtures_footballdata():
    """
    Usage: /soccer/fixtures_footballdata?competition=2021
    (2021 => EPL)
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
        return jsonify(response.json()), response.status_code
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
