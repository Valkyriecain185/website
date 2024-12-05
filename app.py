from flask import Flask, request, render_template, redirect, url_for, session, flash
from authlib.integrations.flask_client import OAuth
from flask_session import Session
import json
import os
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Strong, unique secret key for session management.

# Use filesystem-based session storage
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Admin credentials
ADMIN_PASSWORD = "1322"  # Replace this with your desired admin password.

# Discord OAuth2 setup
DISCORD_CLIENT_ID = '1313855855619473501'
DISCORD_CLIENT_SECRET = 'ji3QW45GiXYpihk3J712vQz_OkRv_fGH'
DISCORD_REDIRECT_URI = 'http://just-another-discord-bot.co.uk/login/callback'

oauth = OAuth(app)
discord = oauth.register(
    name='discord',
    client_id=DISCORD_CLIENT_ID,
    client_secret=DISCORD_CLIENT_SECRET,
    access_token_url='https://discord.com/api/oauth2/token',
    authorize_url='https://discord.com/api/oauth2/authorize',
    api_base_url='https://discord.com/api/',
    client_kwargs={
        'scope': 'identify guilds'
    }
)

# Storage file for YouTube channels, notification channels, counting channels, and tickets
youtube_data_file = 'youtube_data.json'

# Load stored data or initialize new storage
if os.path.exists(youtube_data_file):
    with open(youtube_data_file, 'r') as file:
        youtube_data = json.load(file)
else:
    youtube_data = {
        "server_data": {}
    }

@app.route('/')
def home():
    # Redirect the user to select a server before showing the home page
    if 'selected_server' not in session:
        flash('Please select a server to configure.', 'danger')
        return redirect(url_for('select_server'))
    return render_template('home.html')

@app.route('/youtube-channels', methods=['GET', 'POST'])
def youtube_channels():
    if 'selected_server' not in session:
        flash('Please select a server to configure.', 'danger')
        return redirect(url_for('select_server'))

    guild_id = session['selected_server']
    if guild_id not in youtube_data["server_data"]:
        youtube_data["server_data"][guild_id] = {
            "channels": [],
            "notification_channels": [],
            "counting_channels": [],
            "ticket_panels": []
        }

    guild_config = youtube_data["server_data"][guild_id]

    if request.method == 'POST':
        if 'add_channel' in request.form:
            channel_id = request.form['channel_id']
            if channel_id not in guild_config["channels"]:
                guild_config["channels"].append(channel_id)
                save_youtube_data()
        elif 'delete_channel' in request.form:
            channel_id = request.form['channel_id']
            if channel_id in guild_config["channels"]:
                guild_config["channels"].remove(channel_id)
                save_youtube_data()

    return render_template('youtube_channels.html', youtube_channels=guild_config["channels"])

@app.route('/notification-channels', methods=['GET', 'POST'])
def notification_channels():
    if 'selected_server' not in session:
        flash('Please select a server to configure.', 'danger')
        return redirect(url_for('select_server'))

    guild_id = session['selected_server']
    if guild_id not in youtube_data["server_data"]:
        youtube_data["server_data"][guild_id] = {
            "channels": [],
            "notification_channels": [],
            "counting_channels": [],
            "ticket_panels": []
        }

    guild_config = youtube_data["server_data"][guild_id]

    if request.method == 'POST':
        if 'add_channel' in request.form:
            channel_id = request.form['notification_channel']
            if channel_id not in guild_config["notification_channels"]:
                guild_config["notification_channels"].append(channel_id)
                save_youtube_data()
        elif 'delete_channel' in request.form:
            channel_id = request.form['notification_channel']
            if channel_id in guild_config["notification_channels"]:
                guild_config["notification_channels"].remove(channel_id)
                save_youtube_data()

    return render_template('notification_channels.html', notification_channels=guild_config["notification_channels"])

@app.route('/counting-game', methods=['GET', 'POST'])
def counting_game():
    if 'selected_server' not in session:
        flash('Please select a server to configure.', 'danger')
        return redirect(url_for('select_server'))

    guild_id = session['selected_server']
    if guild_id not in youtube_data["server_data"]:
        youtube_data["server_data"][guild_id] = {
            "channels": [],
            "notification_channels": [],
            "counting_channels": [],
            "ticket_panels": []
        }

    guild_config = youtube_data["server_data"][guild_id]

    if request.method == 'POST':
        if 'add_counting_channel' in request.form:
            channel_id = request.form['counting_channel']
            if channel_id not in guild_config["counting_channels"]:
                guild_config["counting_channels"].append(channel_id)
                save_youtube_data()
        elif 'delete_counting_channel' in request.form:
            channel_id = request.form['counting_channel']
            if channel_id in guild_config["counting_channels"]:
                guild_config["counting_channels"].remove(channel_id)
                save_youtube_data()

    return render_template('counting_game.html', counting_channels=guild_config["counting_channels"])

@app.route('/ticket-settings', methods=['GET', 'POST'])
def ticket_settings():
    if 'selected_server' not in session:
        flash('Please select a server to configure.', 'danger')
        return redirect(url_for('select_server'))

    guild_id = session['selected_server']
    if guild_id not in youtube_data["server_data"]:
        youtube_data["server_data"][guild_id] = {
            "channels": [],
            "notification_channels": [],
            "counting_channels": [],
            "ticket_panels": []
        }

    guild_config = youtube_data["server_data"][guild_id]

    if request.method == 'POST':
        if 'create_ticket_panel' in request.form:
            panel_title = request.form['panel_title']
            panel_description = request.form['panel_description']
            channel_id = request.form['target_channel']
            
            # Store the ticket panel information
            new_panel = {
                "title": panel_title,
                "description": panel_description,
                "channel_id": channel_id
            }
            guild_config["ticket_panels"].append(new_panel)
            save_youtube_data()

            # Notify success
            flash('Ticket panel created successfully. It will be sent to the specified Discord channel.', 'success')

    return render_template('ticket_settings.html', ticket_panels=guild_config["ticket_panels"])

@app.route('/admin-log')
def admin_log():
    if 'logged_in' not in session:
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('home'))
    
    return render_template('admin_log.html', server_data=youtube_data["server_data"])

@app.route('/login')
def login():
    return discord.authorize_redirect(redirect_uri=DISCORD_REDIRECT_URI)

@app.route('/login/callback')
def login_callback():
    try:
        token = discord.authorize_access_token()
        if token is None:
            flash('Access denied.', 'danger')
            return redirect(url_for('home'))

        session['discord_token'] = token
        user_info = discord.get('/users/@me').json()
        session['user'] = user_info

        flash(f"Welcome, {user_info['username']}!", 'success')
        return redirect(url_for('select_server'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/select-server')
def select_server():
    if 'discord_token' not in session:
        flash('Please log in to continue.', 'danger')
        return redirect(url_for('login'))

    headers = {
        "Authorization": f"Bearer {session['discord_token']['access_token']}"
    }
    guilds = requests.get("https://discord.com/api/users/@me/guilds", headers=headers).json()

    # Filter the guilds to only include the ones where the user has administrative permissions
    admin_guilds = [
        guild for guild in guilds
        if (guild['permissions'] & 0x8) == 0x8  # Bitwise operation to check if the user has ADMINISTRATOR permission (bitwise value 0x8)
    ]

    selected_server = session.get('selected_server')

    return render_template('select_server.html', guilds=admin_guilds, selected_server=selected_server)

@app.route('/configure-server/<guild_id>')
def configure_server(guild_id):
    if 'discord_token' not in session:
        flash('Please log in to continue.', 'danger')
        return redirect(url_for('login'))

    session['selected_server'] = guild_id
    guild_config = youtube_data["server_data"].get(guild_id, {
        "channels": [],
        "notification_channels": [],
        "counting_channels": [],
        "ticket_panels": []
    })
    return render_template('configure_server.html', guild_config=guild_config)

@app.route('/save-server-config', methods=['POST'])
def save_server_config():
    if 'selected_server' not in session:
        flash('Please select a server to configure.', 'danger')
        return redirect(url_for('select_server'))

    guild_id = session['selected_server']
    if guild_id not in youtube_data["server_data"]:
        youtube_data["server_data"][guild_id] = {
            "channels": [],
            "notification_channels": [],
            "counting_channels": [],
            "ticket_panels": []
        }

    # Save configurations
    youtube_data["server_data"][guild_id]["channels"] = request.form.getlist("youtube_channels")
    youtube_data["server_data"][guild_id]["notification_channels"] = request.form.getlist("notification_channels")
    youtube_data["server_data"][guild_id]["counting_channels"] = request.form.getlist("counting_channels")
    youtube_data["server_data"][guild_id]["ticket_panels"] = json.loads(request.form.get("ticket_panels", "[]"))

    save_youtube_data()
    flash('Configuration saved successfully.', 'success')
    return redirect(url_for('configure_server', guild_id=guild_id))

# Helper function to save YouTube data
def save_youtube_data():
    with open(youtube_data_file, 'w') as file:
        json.dump(youtube_data, file)

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000, debug=True)

