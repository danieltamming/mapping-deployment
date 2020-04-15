import os
import pickle
from datetime import datetime, timedelta, date

import geopy.distance

from tqdm import tqdm
import matplotlib.pyplot as plt
import networkx as nx
from networkx.readwrite.gpickle import read_gpickle, write_gpickle

from dataframe import get_stops_within
# from utils import get_travel_time


def get_travel_time(p1, p2, km_per_min=5/60):
	'''
	Calculates time to walk from p1 to p2, 
	where both points are latitude longitude pairs
	'''
	km_per_sec = km_per_min/60
	dist = geopy.distance.distance(p1, p2).km
	return int(dist/km_per_sec)

def add_temp_stops(DG, stops, start_stop_ids, end_stop_ids, 
				   start_coord, end_coord):
	to_remove = ['temp start', 'temp end']
	for stop_id_A in start_stop_ids:
		nodes_A = [key for key in DG.nodes.keys() if key[0] == stop_id_A]
		temp_node_A = (stop_id_A, -1)
		for node_A in nodes_A:
			DG.add_edge(temp_node_A, node_A, weight=0, path=(-1, -1))
		stop_coord_A = stops.loc[stop_id_A][['stop_lat', 'stop_lon']].values
		walk_time = get_travel_time(start_coord, stop_coord_A)
		DG.add_edge('temp start', temp_node_A, 
					weight=walk_time, path=(-1, -1))
		to_remove.append(temp_node_A)
	for stop_id_B in end_stop_ids:
		nodes_B = [key for key in DG.nodes.keys() if key[0] == stop_id_B]
		temp_node_B = (stop_id_B, -1)
		for node_B in nodes_B:
			DG.add_edge(node_B, temp_node_B, weight=0, path=(-1, -1))
		stop_coord_B = stops.loc[stop_id_B][['stop_lat', 'stop_lon']].values
		walk_time = get_travel_time(stop_coord_B, end_coord)
		DG.add_edge(temp_node_B, 'temp end', weight=walk_time, path=(-1, -1))
		to_remove.append(temp_node_B)
	return to_remove

def remove_temp_stops(DG, to_remove):
	for node in to_remove:
		DG.remove_node(node)

def my_add_node(DG, stop_id, stop_lon, stop_lat, wait_time=7*60):
	'''
	Each stop_id can have multiple nodes that should be connected
	by an edge, so add node and connect it to all nodes that share
	this stop_id
	'''
	idx = 0
	while DG.has_node((stop_id, idx)):
		idx += 1
	DG.add_node((stop_id, idx), pos=(stop_lon, stop_lat))
	for i in range(idx):
		DG.add_edge((stop_id, i), (stop_id, idx), 
					weight=wait_time, path=(-1, -1))
		DG.add_edge((stop_id, idx), (stop_id, i), 
					weight=wait_time, path=(-1, -1))
	return (stop_id, idx)

def add_edges_between_stop_ids(my_df, DG, stop_A, stop_B, wait_time):
	'''
	Each stop_id can have multiple nodes, so add edges between all 
	pairs of nodes between two stop_ids
	'''
	A_coords = my_df[my_df['stop_id'] == stop_A][
		['stop_lat', 'stop_lon']].drop_duplicates().values[0]
	B_coords = my_df[my_df['stop_id'] == stop_B][
		['stop_lat', 'stop_lon']].drop_duplicates().values[0]
	total_time = wait_time + get_travel_time(A_coords, B_coords)
	i = 0
	while (stop_A, i) in DG.nodes:
		j = 0
		while (stop_B, j) in DG.nodes:
			if not DG.has_edge((stop_A, i), (stop_B, j)):
				DG.add_edge((stop_A, i), (stop_B, j), 
							weight=total_time, path=(-1, -1))
			if not DG.has_edge((stop_B, j), (stop_A, i)):
				DG.add_edge((stop_B, j), (stop_A, i), 
							weight=total_time, path=(-1, -1))
			j += 1
		i += 1

def add_walkable(my_df, DG, wait_time=7*60, max_dist=0.1):
	'''
	Add edges between all nodes within 0.1 km of one another
	'''
	for stop_id in tqdm(my_df['stop_id'].values):
		if (stop_id, 0) not in DG.nodes:
			continue
		close_stop_ids = get_stops_within(my_df, stop_id, max_dist)
		for near_id in close_stop_ids:
			if near_id != stop_id:
				add_edges_between_stop_ids(my_df, DG, stop_id, 
										   near_id, wait_time)
	return DG

def construct_graph(my_df):
	DG = nx.DiGraph()
	route_direction_pairs = set(
		tuple(L) for L in my_df[['route_id', 'direction_id']].values.tolist())
	for route_id, direction_id in route_direction_pairs:
		this_route = my_df.loc[(my_df['route_id'] == route_id)
							 & (my_df['direction_id'] == direction_id)]
		travel_times = this_route['time'].map(
			lambda x : datetime.combine(date.min, x)).diff().map(
				lambda x : x.total_seconds()).values
		stop_ids = this_route['stop_id'].values
		stop_coords = this_route[['stop_lat', 'stop_lon']].values
		prev_stop_id = stop_ids[0]
		stop_lat, stop_lon = stop_coords[0]
		prev_key = my_add_node(DG, prev_stop_id, stop_lon, stop_lat)
		for end_idx in range(1, len(travel_times)):
			cur_stop_id = stop_ids[end_idx]
			stop_lat, stop_lon = stop_coords[end_idx]
			travel_time = travel_times[end_idx]
			cur_key = my_add_node(DG, cur_stop_id, stop_lon, stop_lat)
			DG.add_edge(prev_key, cur_key, weight=travel_time, 
						path=(route_id, direction_id))
			prev_key = cur_key
	return DG

def show_graph(DG):
	colors = ['g' if DG.edges[(u, v)]['path'] == (-1, -1) 
			  else 'b' for u, v in DG.edges]
	nx.draw(DG, nx.get_node_attributes(DG, 'pos'), 
			node_size=5, node_color='r', width=1, 
			edge_color=colors, arrowsize=8, with_labels=False)
	# nx.draw_networkx_labels(DG, pos, pos)
	plt.show()

def get_graph(my_df, saving=True):
	graph_filename = 'data/graph.pickle'
	if saving and os.path.exists(graph_filename):
		print('Loading graph from file.')
		return read_gpickle(graph_filename)
	print('Constructing and saving graph. Should take a few minutes.')
	DG = construct_graph(my_df)
	DG = add_walkable(my_df, DG)
	if saving: write_gpickle(DG, graph_filename, pickle.HIGHEST_PROTOCOL)
	return DG