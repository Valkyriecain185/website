from flask import Flask, request, jsonify, session, redirect, url_for, flash
from authlib.integrations.flask_client import OAuth
from flask_session import Session
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Session Setup
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# OAuth Configuration for Discord
DISCORD_CLIENT_ID = 'Your_Discord_Client_ID'
DISCORD_CLIENT_SECRET = 'Your_Discord_Client_Secret'
DISCORD_REDIRECT_URI = 'https://your-backend-url.com/login/callback'

oauth = OAuth(app)
discord = oauth.register(
    name='discord',
    client_id=DISCORD_CLIENT_ID,
    client_secret=DISCORD_CLIENT_SECRET,
    access_token_url='https://discord.com/api/oauth2/token',
    authorize_url='https://discord.com/api/oauth2/authorize',
    api_base_url='https://discord.com/api/',
    client_kwargs={'scope': 'identify guilds'}
)

youtube_data_file = 'youtube_data.json'
if os.path.exists(youtube_data_file):
    with open(youtube_data_file, 'r') as file:
        youtube_data = json.load(file)
else:
    youtube_data = {"server_data": {}}

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to Discord Bot Backend'})

@app.route('/login')
def login():
    return discord.authorize_redirect(redirect_uri=DISCORD_REDIRECT_URI)

@app.route('/login/callback')
def login_callback():
    token = discord.authorize_access_token()
    session['discord_token'] = token
    return redirect(url_for('select_server'))

@app.route('/select-server')
def select_server():
    headers = {"Authorization": f"Bearer {session['discord_token']['access_token']}"}
    guilds = requests.get("https://discord.com/api/users/@me/guilds", headers=headers).json()
    return jsonify(guilds)

@app.route('/api/servers')
def api_servers():
    # Example endpoint to return server list for the frontend
    return jsonify([{"id": "123", "name": "Test Server"}])  # Dummy data, replace as necessary

# Save youtube_data.json
def save_youtube_data():
    with open(youtube_data_file, 'w') as file:
        json.dump(youtube_data, file)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
