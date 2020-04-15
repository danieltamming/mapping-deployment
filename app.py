import requests
from flask import Flask, jsonify, request
import os

from path import Path
from gmaps import get_gmaps_route, get_gmaps_coords
from utils import get_all_data, get_meeting_location
from keys import ACCESS_TOKEN, VERIFY_TOKEN

def get_response(message):
	if len(message.split('.', 2)) != 3:
		return ('Please try again. Send the driver\'s location, the'
				' pedestrian\'s location, and their shared final destination,'
				' separated by periods.')
	start_pedestrian, start_drive, end_drive = message.split('.', 2)
	start_coord, start_address = get_gmaps_coords(start_pedestrian)
	lat, lng = start_coord
	if lat > top or lat < bottom or lng < left or lng > right:
		return ('Pedestrian must be within range of Toronto Public Transit.'
				' Please try again.')
	(start_address, end_address, polies, 
		points) = get_gmaps_route(A=start_drive, B=end_drive)
	if start_address == -1:
		return ('Travel between the driver\'s starting location and the shared'
				' final destination must be possible by automobile.'
				' Please try again.')
	meetup_location = get_meeting_location(
		DG, my_df, stops, start_coord, polies[::20], trip_names)
	return 'You should meet at: ' + meetup_location

top = 43.90975
left = -79.649908
bottom = 43.591811
right = -79.123111
my_df, stops, trip_names, DG = get_all_data()

FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
# ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
# VERIFY_TOKEN = os.environ['VERIFY_TOKEN']

app = Flask(__name__)

def send_message(recipient_id, text):
    """Send a response to Facebook"""
    payload = {'message':{'text': text}, 'recipient': {'id': recipient_id}, 
    			'notification_type': 'regular'}
    auth = {'access_token': ACCESS_TOKEN}
    response = requests.post(FB_API_URL, params=auth, json=payload)
    return response.json()

def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"

def respond(sender, message):
    """Formulate a response to the user and
    pass it on to a function that sends it."""
    response = get_response(message)
    send_message(sender, response)


def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))

@app.route('/webhook', methods=['GET','POST'])
def listen():
	if request.method == 'GET':
		return verify_webhook(request)

	if request.method == 'POST':
		file = request.json
		event = file['entry'][0]['messaging']
		for x in event:
			if is_user_message(x):
				text = x['message']['text']
				sender_id = x['sender']['id']
				respond(sender_id, text)
		return 'ok'

if __name__ == "__main__":
    app.run()