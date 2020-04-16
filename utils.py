import math
import bisect

import geopy.distance
import networkx.algorithms.shortest_paths.weighted as algos
from tqdm import tqdm

from gmaps import get_gmaps_route, get_gmaps_coords
from graphing import get_graph, add_temp_stops, remove_temp_stops
from dataframe import get_df, get_stops, get_trip_names, get_closest_stops
from path import Path


def get_best_route(DG, my_df, stops, start_coord, end_coord, num_stops):
	'''
	Find optimal commuter path between start_coord and end_coord.
	Considers beginning travel at a num_stops number of transit 
	stops that are closest to the starting coordinate. 
	'''
	WAIT_TIME = 7*60

	start_stop_ids = get_closest_stops(my_df, start_coord, num_stops)
	end_stop_ids = get_closest_stops(my_df, end_coord, num_stops)
	to_remove = add_temp_stops(DG, stops, start_stop_ids, end_stop_ids,
							   start_coord, end_coord)
	result = algos.dijkstra_path(DG, 'temp start', 
								'temp end', weight='weight')
	assert (isinstance(result[0], str) and isinstance(result[-1], str)
			and result[1][1] == -1 and result[-2][1] == -1)
	path = Path(DG, result, WAIT_TIME)
	remove_temp_stops(DG, to_remove)
	return path

def get_all_data():
	'''
	Retrieves (or creates, if necessary) the three dataframes 
	and one graph that are essential to all computations
	'''
	my_df = get_df(saving=True)
	stops = get_stops()
	trip_names = get_trip_names()
	DG = get_graph(my_df, saving=True)
	return my_df, stops, trip_names, DG

def get_travel_time(p1, p2, km_per_min=5/60):
	'''
	Calculates time to walk from p1 to p2, 
	where both points are latitude longitude pairs
	'''
	km_per_sec = km_per_min/60
	dist = geopy.distance.distance(p1, p2).km
	return int(dist/km_per_sec)

def plot_temp(polies):
	ys = [pol[0] for pol in polies]
	xs = [pol[1] for pol in polies]
	plt.scatter(xs, ys)
	plt.show()

def get_user_input():
	# lat = input('Enter pedestrian latitude coordinate: ')
	# lon = input('Enter pedestrian longitude coordinate: ')
	# start_coord = (lat, lon)
	# print('\nDriver locations may be entered in any format acceptable'
	# 	  ' by Google Maps (e.g. Pearson Airport).')
	# return (lat, lon), start_drive, end_drive
	start_pedestrian = input('Enter pedestrian starting location: ')
	start_drive = input('Enter driver starting location: ')
	end_drive = input('Enter ending location: ')
	return start_pedestrian, start_drive, end_drive

def get_example():
	start_coord = (43.655900, -79.492757)
	(start_address, end_address, polies, 
		_) = get_gmaps_route(example=True)
	print('Driver\'s starting address: ' + start_address)
	print('Pedestrian\'s starting coordinates: {}'.format(start_coord))
	print('Joint ending address: ' + end_address)
	return polies, start_coord

def get_custom():
	approved = False
	while not approved:
		start_pedestrian, start_drive, end_drive = get_user_input()
		start_coord, start_address = get_gmaps_coords(start_pedestrian)
		usr_input = input('Correct pedestrian start? (Y/N) '
			+ start_address + '\n').lower()
		if usr_input != 'y':
			print('\nRestarting input process.')
			continue
		(start_address, end_address, polies, 
			points) = get_gmaps_route(A=start_drive, B=end_drive, saving=True)
		usr_input = input('Correct driver start? (Y/N) ' 
			+ start_address + '\n').lower()
		if usr_input != 'y':
			print('\nRestarting input process.')
			continue
		usr_input = input('Correct driver end? (Y/N) ' 
			+ end_address + '\n').lower()
		if usr_input != 'y':
			print('\nRestarting input process.')
			continue
		approved = True
	return polies, start_coord

def get_use_type():
	usr_input = 0
	while usr_input not in [1, 2]:
		usr_input = input('Enter 1 for an example, or 2 for custom input: ')
		if usr_input.isdigit():
			usr_input = int(usr_input)
	if usr_input == 1:
		return get_example()
	else:
		return get_custom()

def get_calc_time(my_df, DG, stops):
	'''
	Used in computation time testing. Calculates the average 
	time it takes to find optimal routes between various points
	'''

	# coordinates that form an approximate bounding box around Toronto
	top = 43.716832
	left = -79.543279
	bottom = 43.665441
	right = -79.331792
	num_points = 5
	lats = np.linspace(bottom, top, num=num_points)
	lons = np.linspace(left, right, num=num_points)
	count = 0
	start_time = time.time()
	for i in range(len(lats)-1):
		for j in range(len(lons)-1):
			for k in range(i+1, len(lats)):
				for l in range(j+1, len(lons)):
					A = (lats[i], lons[j])
					B = (lats[k], lons[l])
					get_best_route(DG, my_df, stops, A, B, 8)
					get_best_route(DG, my_df, stops, B, A, 8)
					count += 2
	delta_time = time.time() - start_time
	print(count)
	print(round(delta_time, 2))
	print(round(delta_time/count, 2))

def get_points():
	usr_input = input('Enter pedestrian starting location,'
					  ' driver starting location, '
					  'driving ending location: ')
	start_pedestrian, start_drive, end_drive = usr_input.split('. ')
	start_coord, start_address = get_gmaps_coords(start_pedestrian)
	(start_address, end_address, polies, 
		points) = get_gmaps_route(A=start_drive, B=end_drive, saving=True)
	return polies, start_coord

def prune_coords(coords):
	'''
	Removes coordinates that are outside the range of Toronto Transit
	Makes coordinate list no longer than max_len
	Does not preserve order
	'''
	max_len = 30
	transit_top = 43.90975
	transit_left = -79.649908
	transit_bottom = 43.591811
	transit_right = -79.123111
	orig = coords.copy()

	coords = [(lat, lon, idx) for idx, (lat, lon) in enumerate(coords)]
	coords = sorted(coords, key=lambda tup: tup[1])
	left_idx = bisect.bisect_left([lon for (lat, lon, idx) in coords], transit_left)
	coords = coords[left_idx:]
	right_idx = bisect.bisect_right([lon for (lat, lon, idx) in coords], transit_right)
	coords = coords[:right_idx]
	coords = sorted(coords, key=lambda tup: tup[0])
	bottom_idx = bisect.bisect_left([lat for (lat, lon, idx) in coords], transit_bottom)
	coords = coords[bottom_idx:]
	top_idx = bisect.bisect_right([lat for (lat, lon, idx) in coords], transit_top)
	coords = coords[:top_idx]
	coords = sorted(coords, key=lambda tup: tup[2])
	coords = [(lat, lon) for (lat, lon, idx) in coords]
	if not coords:
		return -1
	ls1 = [element for element in orig if element in coords]
	ls2 = [element for element in coords if element in orig]
	assert ls1 == ls2
	# make list no longer than max_len
	k = math.ceil(len(coords) / max_len)
	coords = coords[::k]
	return coords

def get_meeting_location(DG, my_df, stops, start_coord, 
						 drive_coords, trip_names):
	drive_coords = prune_coords(drive_coords)
	if drive_coords == -1:
		return -1
	best_time = float('inf')
	for end_coord in tqdm(drive_coords):
		path = get_best_route(DG, my_df, stops, start_coord, end_coord, 8)
		if path.travel_time < best_time:
			best_time = path.travel_time
			best_path = path
	return best_path.get_meetup_location(stops, trip_names)