import os
import pickle

import googlemaps
import polyline

from path import Path

# from keys import API_KEY
API_KEY = os.environ['API_KEY']

def get_gmaps_route(A=None, B=None, saving=False, example=False):
	# assert os.path.exists('keys.py') , 'Need Google API key. See README.'
	gmaps = googlemaps.Client(key=API_KEY)
	try:
		result = gmaps.directions(A, B, mode='driving', units='metric')
		# result = pickle.load(open('temp.pickle', 'rb'))
	except:
		return (-1, -1, -1, -1, -1, -1)
	if not result:
		return (-1, -1, -1, -1, -1, -1)
	polies = []
	points = []
	for i, step in enumerate(result[0]['legs'][0]['steps']):
		polies.extend(polyline.decode(step['polyline']['points']))
		lat = step['start_location']['lat']
		lon = step['start_location']['lng']
		points.append((lat, lon))
	points.append((step['end_location']['lat'], step['end_location']['lng']))
	legs = result[0]['legs']
	start_address = legs[0]['start_address']
	start_coord = (legs[0]['start_location']['lat'], 
				   legs[0]['start_location']['lng'])
	end_address = legs[-1]['end_address']
	end_coord = (legs[-1]['end_location']['lat'], 
				   legs[-1]['end_location']['lng'])
	return start_address, end_address, polies, points, start_coord, end_coord

def get_gmaps_coords(location_str):
	gmaps = googlemaps.Client(key=API_KEY)
	query = gmaps.geocode(location_str)
	location = query[0]['geometry']['location']
	address = query[0]['formatted_address']
	return (location['lat'], location['lng']), address