import os
from datetime import datetime, timedelta, date

from tqdm import tqdm
import numpy as np
import pandas as pd
import geopy.distance
from scipy.spatial.distance import cdist

def get_closest_stops(my_df, coords, k=1):
	'''
	Find the k nearest stop_ids that have unique route_ids
	Returns stop_ids, route_id, direction_id
	'''
	lat, lon = coords
	# fast way to get order approximated by euclidean distance
	approx_order = cdist([[lat, lon]], 
					my_df[['stop_lat', 'stop_lon']]).argsort()[0,:]
	# assume k closest points will be in first 10*k indices of approx
	approx_df = my_df.iloc[approx_order[:10*k], :]
	order = np.apply_along_axis(
		lambda row: geopy.distance.distance(coords, row).km, 1, 
		approx_df[['stop_lat', 'stop_lon']].values).argsort()
	# order will include indices of rows with same stop_id, different route
	# and direction
	ordered_df = approx_df.iloc[order, :][
		['stop_id', 'route_id', 'direction_id']].values
	lines_seen = set()
	closest_stop_ids = []
	for stop_id, route_id, direction_id in ordered_df:
		if ((route_id, direction_id) not in lines_seen 
				and stop_id not in closest_stop_ids):
			closest_stop_ids.append(stop_id)
			lines_seen.add((route_id, direction_id))
		if len(closest_stop_ids) >= k:
			break
	return closest_stop_ids

def get_stops_within(my_df, stop_id, max_dist):
	stops = my_df[['stop_id', 'stop_lat', 'stop_lon']].drop_duplicates()
	lat, lon = stops.loc[
		stops['stop_id'] == stop_id][['stop_lat', 'stop_lon']].iloc[0].values
	order = cdist([[lat, lon]],
					stops[['stop_lat', 'stop_lon']]).argsort()[0,:]
	idxs = []
	for i in order:
		point = tuple(stops.iloc[i][['stop_lat', 'stop_lon']].values)
		if geopy.distance.distance((lat, lon), point).km > max_dist:
			break
		idxs.append(i)
	return stops.iloc[idxs]['stop_id'].values

def to_datetime(s):
	arr = s.split(':')
	add_day = False
	if int(arr[0]) >= 24:
		arr[0] = str(int(arr[0]) - 24)
		add_day = True
	dtime = datetime.strptime(':'.join(arr), '%H:%M:%S')
	if add_day:
		dtime = dtime + timedelta(days=1)
	return dtime

def get_stops():
	stops_filepath = 'data/stops.txt'
	return pd.read_csv(
		stops_filepath)[
			['stop_id', 'stop_name', 'stop_lat', 'stop_lon']
			].set_index('stop_id')

def get_trip_names():
	trips_filepath = 'data/trips.txt'
	return pd.read_csv(trips_filepath)[
		['route_id', 'direction_id', 'trip_headsign']
		].drop_duplicates().set_index('route_id')

def get_df(saving=True):
	folder = 'OpenData_TTC_Schedules/'
	my_df_filepath = 'data/my_df.csv'
	if saving and os.path.exists(my_df_filepath):
		print('Loading dataframe from file.')
		df = pd.read_csv(my_df_filepath)
		df['time'] = df['time'].map(lambda x : to_datetime(x).time())
		return df