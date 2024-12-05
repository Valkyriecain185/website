from flask import Flask, request, render_template, redirect, url_for, session, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'huxley1888'  # <-- Replace with a strong, unique secret key for session management.

# Admin credentials
ADMIN_PASSWORD = "1322"  # <-- Replace this with your desired admin password.

# Storage file for YouTube channels, notification channels, counting channels, and tickets
youtube_data_file = 'youtube_data.json'

# Load stored data or initialize new storage
if os.path.exists(youtube_data_file):
    with open(youtube_data_file, 'r') as file:
        youtube_data = json.load(file)

    # Ensure keys are present in older files
    if "counting_channels" not in youtube_data:
        youtube_data["counting_channels"] = []
    if "ticket_panels" not in youtube_data:
        youtube_data["ticket_panels"] = []
else:
    youtube_data = {
        "channels": [],
        "notification_channels": [],
        "counting_channels": [],  # List of counting channels
        "ticket_panels": []  # List of ticket panel configurations
    }

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/youtube-channels', methods=['GET', 'POST'])
def youtube_channels():
    if request.method == 'POST':
        if 'add_channel' in request.form:
            channel_id = request.form['channel_id']
            if channel_id not in youtube_data["channels"]:
                youtube_data["channels"].append(channel_id)
                save_youtube_data()
        elif 'delete_channel' in request.form:
            channel_id = request.form['channel_id']
            if channel_id in youtube_data["channels"]:
                youtube_data["channels"].remove(channel_id)
                save_youtube_data()
    return render_template('youtube_channels.html', youtube_channels=youtube_data["channels"])

@app.route('/ticket-settings', methods=['GET', 'POST'])
def ticket_settings():
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
            youtube_data["ticket_panels"].append(new_panel)
            save_youtube_data()

            # Notify success
            flash('Ticket panel created successfully. It will be sent to the specified Discord channel.', 'success')
    
    return render_template('ticket_settings.html', ticket_panels=youtube_data["ticket_panels"])

@app.route('/notification-channels', methods=['GET', 'POST'])
def notification_channels():
    if request.method == 'POST':
        if 'add_channel' in request.form:
            channel_id = request.form['notification_channel']
            if channel_id not in youtube_data["notification_channels"]:
                youtube_data["notification_channels"].append(channel_id)
                save_youtube_data()
        elif 'delete_channel' in request.form:
            channel_id = request.form['notification_channel']
            if channel_id in youtube_data["notification_channels"]:
                youtube_data["notification_channels"].remove(channel_id)
                save_youtube_data()
    return render_template('notification_channels.html', notification_channels=youtube_data["notification_channels"])

@app.route('/counting-game', methods=['GET', 'POST'])
def counting_game():
    if request.method == 'POST':
        if 'add_counting_channel' in request.form:
            channel_id = request.form['counting_channel']
            if channel_id not in youtube_data["counting_channels"]:
                youtube_data["counting_channels"].append(channel_id)
                save_youtube_data()
        elif 'delete_counting_channel' in request.form:
            channel_id = request.form['counting_channel']
            if channel_id in youtube_data["counting_channels"]:
                youtube_data["counting_channels"].remove(channel_id)
                save_youtube_data()
    return render_template('counting_game.html', counting_channels=youtube_data["counting_channels"])

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/admin-log', methods=['GET', 'POST'])
def admin_log():
    if 'logged_in' not in session:
        if request.method == 'POST':
            password = request.form['password']
            if password == ADMIN_PASSWORD:
                session['logged_in'] = True
                return redirect(url_for('admin_log'))
            else:
                flash('Invalid password, please try again.', 'danger')
        return render_template('admin_login.html')

    return render_template('admin_log.html', youtube_channels=youtube_data["channels"], notification_channels=youtube_data["notification_channels"], counting_channels=youtube_data["counting_channels"], ticket_panels=youtube_data["ticket_panels"])

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

def save_youtube_data():
    with open(youtube_data_file, 'w') as file:
        json.dump(youtube_data, file)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
