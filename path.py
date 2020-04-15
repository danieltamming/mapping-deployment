import time

import matplotlib.pyplot as plt
import osmnx as ox
import networkx as nx
from networkx.classes.graphviews import subgraph_view

class Path:
	def __init__(self, DG, path, wait_time):
		self.DG = DG
		self.wait_time = wait_time
		self.path = path
		self.segments = self.process_path(self.path)
		self.travel_time = self._get_travel_time()

	def _get_travel_time(self):
		return sum([seg['travel_time'] for seg in self.segments])

	def _get_start_walk_segment(self, path):
		temp_edge_walk_time = sum(
			self.DG.edges[(path[idx],path[idx+1])]['weight'] for idx in [0,1])
		path = path[2:]
		seg = {'start' : -1, 'line' : (-1, -1), 
			   'travel_time' : temp_edge_walk_time}
		while (len(path) >= 2 
				and self.DG.edges[(path[0], path[1])]['path'] == (-1, -1)):
			seg['travel_time'] += (self.DG.edges[(path[0], path[1])]['weight'] 
								   - self.wait_time)
			assert seg['travel_time'] >= 0
			path = path[1:]
		seg['end'] = path[0]
		assert len(path) >= 2
		return path, seg

	def _get_end_walk_segment(self, path):
		temp_edge_walk_time = sum(
			self.DG.edges[path[idx-1],path[idx]]['weight'] for idx in [-1,-2])
		path = path[:-2]
		idx = len(path) - 2
		seg = {'end' : -1, 'line' : (-1, -1), 
			   'travel_time' : temp_edge_walk_time}
		while self.DG.edges[(path[idx], path[idx+1])]['path'] == (-1, -1):
			weight = self.DG.edges[(path[idx], path[idx+1])]['weight']
			seg['travel_time'] += weight - self.wait_time
			assert seg['travel_time'] >= 0
			idx -= 1
		seg['start'] = path[idx]
		path = path[:idx+1]
		return path, seg

	def _get_middle_segments(self, path):
		segments = []
		first_line = self.DG.edges[(path[0], path[1])]['path']
		seg = {'start' : path[0], 'line' : first_line, 'travel_time' : 0}
		prev_line = -1
		for edge in zip(path[1:-1], path[2:]):
			line = self.DG.edges[edge]['path']
			travel_time = self.DG.edges[edge]['weight']
			if line == (-1, -1):
				seg['end'] = edge[0]
				segments.append(seg)
				segments.append({'start' : edge[0], 
								 'line': (-1, -1),
								 'travel_time' : travel_time,
								 'end' : edge[1]})
			elif prev_line == (-1, -1):
				assert line != (-1, -1)
				seg = {'start' : edge[0], 'line' : line, 
					   'travel_time' : travel_time}
			else:
				seg['travel_time'] += travel_time
			prev_line = line
		seg['end'] = path[-1]
		segments.append(seg)
		return segments


	def process_path(self, path):
		# these three functions must be called in this order
		path, start_walk_seg = self._get_start_walk_segment(path)
		path, end_walk_seg = self._get_end_walk_segment(path)
		segments = self._get_middle_segments(path)
		if start_walk_seg is not None:
			segments.insert(0, start_walk_seg)
		if end_walk_seg is not None:
			segments.append(end_walk_seg)
		return segments

	def get_meetup_location(self, stops, trip_names):
		seg = self.segments[-2]
		end_stop_id = seg['end'][0]
		stop_name = stops.loc[end_stop_id]['stop_name']
		return ' '.join([word.capitalize() for word in stop_name.split()])