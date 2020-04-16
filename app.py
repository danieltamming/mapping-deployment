import requests
from flask import Flask, jsonify, request
import os

from path import Path
from gmaps import get_gmaps_route, get_gmaps_coords
from utils import get_all_data, get_meeting_location
# from keys import ACCESS_TOKEN, VERIFY_TOKEN

def get_response(message):
	if len(message.split('.', 2)) != 3:
		return ('Please try again. Send the pedestrian\'s location, the'
				' driver\'s location, and their shared final destination,'
				' separated by periods.')
	start_pedestrian, start_drive, end_drive = message.split('.', 2)
	start_coord, start_address = get_gmaps_coords(start_pedestrian)
	lat, lng = start_coord
	if (lat > transit_top or lat < transit_bottom 
			or lng < transit_left or lng > transit_right):
		return ('Pedestrian must be within range of Toronto Public Transit.'
				' Please try again.')
	(start_address, end_address, polies, points, drive_start_coord, 
		end_coord) = get_gmaps_route(A=start_drive, B=end_drive)
	if start_address == -1:
		return ('Travel between the driver\'s starting location and the shared'
				' final destination must be possible by automobile.'
				' Please try again.')
	# for (lat, lng) in [drive_start_coord, end_coord]:
	# 	if (lat > ont_top or lat < ont_bottom 
	# 			or lng < ont_left or lng > ont_right):
	# 		return ('Driver\'s starting location and the shared final'
	# 				' destination must be in Ontario, Canada.'
	# 				' Please try again.')
	meetup_location = get_meeting_location(
		DG, my_df, stops, start_coord, polies, trip_names)
	if meetup_location == -1:
		return ('Driver must be passing through the Greater Toronto Area.'
				' Please try again.')
	return 'Arrange to meet at the following TTC stop: ' + meetup_location
	# return 'Hello'

transit_top = 43.90975
transit_left = -79.649908
transit_bottom = 43.591811
transit_right = -79.123111
# ont_top = 56.86
# ont_left = -95.16
# ont_bottom = 41.66
# ont_right = -74.34

my_df, stops, trip_names, DG = get_all_data()
# print(get_response(input('Enter input: ')))
# exit()

FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']

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