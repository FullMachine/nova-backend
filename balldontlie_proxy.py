from flask import Flask, request, jsonify
import requests

proxy_app = Flask(__name__)

@proxy_app.route('/proxy/nba', methods=['GET'])
def proxy_nba():
    # Retrieve parameters from the request (e.g., player and season)
    player = request.args.get('player')
    season = request.args.get('season')
    if not player or not season:
        return jsonify({'error': 'Missing required parameters. Usage: /proxy/nba?player=lebron%20james&season=2022'}), 400

    # Construct the BallDontLie API URLs (using the official domain)
    search_url = f"https://www.balldontlie.io/api/v1/players?search={player}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }
    
    # Forward the search request
    search_resp = requests.get(search_url, headers=headers)
    try:
        search_data = search_resp.json()
    except Exception as e:
        return jsonify({'error': 'Error parsing JSON from BallDontLie search', 'raw_response': search_resp.text[:500]}), 500

    if not search_data.get('data'):
        return jsonify({'error': 'Player not found'}), 404

    # Get the first matching player ID
    player_id = search_data['data'][0]['id']
    
    # Construct the season averages URL
    stats_url = f"https://www.balldontlie.io/api/v1/season_averages?season={season}&player_ids[]={player_id}"
    stats_resp = requests.get(stats_url, headers=headers)
    try:
        stats_data = stats_resp.json()
    except Exception as e:
        return jsonify({'error': 'Error parsing JSON from season averages', 'raw_response': stats_resp.text[:500]}), 500

    return jsonify(stats_data), 200

if __name__ == '__main__':
    proxy_app.run(host='0.0.0.0', port=8081, debug=True)
