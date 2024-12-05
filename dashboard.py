from flask import Flask, request, render_template, redirect, url_for
import json
import os

app = Flask(__name__)

# Storage file for YouTube channels and notification channel
youtube_data_file = 'youtube_data.json'

# Load stored data or initialize new storage
if os.path.exists(youtube_data_file):
    with open(youtube_data_file, 'r') as file:
        youtube_data = json.load(file)
else:
    youtube_data = {
        "channels": [],
        "notification_channel": None
    }

@app.route('/')
def home():
    return render_template('index.html', youtube_channels=youtube_data["channels"], notification_channel=youtube_data["notification_channel"])

@app.route('/add_channel', methods=['POST'])
def add_channel():
    channel_id = request.form['channel_id']
    if channel_id not in youtube_data["channels"]:
        youtube_data["channels"].append(channel_id)
        save_youtube_data()
    return redirect(url_for('home'))

@app.route('/set_notification_channel', methods=['POST'])
def set_notification_channel():
    channel_id = request.form['notification_channel']
    youtube_data["notification_channel"] = channel_id
    save_youtube_data()
    return redirect(url_for('home'))

def save_youtube_data():
    with open(youtube_data_file, 'w') as file:
        json.dump(youtube_data, file)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
