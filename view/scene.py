from utils.atomic_var import *

import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
import numpy as np
import queue
import time
import threading

# how many metres represents one newton per coulomb
ELECTRIC_FIELD_SCALING = 0.1

fast_forward_rate = 4.0

class Scene(object):
	@classmethod
	def initialize_view(cls):
		cls.ax = plt.axes()
		cls.fig = plt.figure()
		cls.fig.show()

	def __init__(self):
		self.quiver_base_x_list = []
		self.quiver_base_y_list = []
		self.quiver_x_list = []
		self.quiver_y_list = []
		self.quiver_lengths = []
		self.charge_position = [0, 0, 0]

	def update_view(self, field_samples, charge_position):
		self.charge_position = charge_position

		self.quiver_base_x_list = []
		self.quiver_base_y_list = []
		self.quiver_x_list = []
		self.quiver_y_list = []
		self.quiver_lengths = []

		for field_sample in field_samples:
			tail_position = field_sample[0]
			E_vector = np.array(field_sample[1])
			E_vector *= ELECTRIC_FIELD_SCALING
			E_vector_length = np.linalg.norm(E_vector)

			if E_vector_length > 0.0:
				self.quiver_base_x_list.append(tail_position[0])
				self.quiver_base_y_list.append(tail_position[1])
				#scale the vector a unit vector otherwise creetes clutter
				self.quiver_x_list.append(E_vector[0] / E_vector_length)
				self.quiver_y_list.append(E_vector[1] / E_vector_length)
				self.quiver_lengths.append(E_vector_length)

	def plot_quivers(self):
		plt.clf()
		if self.quiver_lengths:
			plt.quiver(self.quiver_base_x_list, self.quiver_base_y_list, self.quiver_x_list, self.quiver_y_list, 
			self.quiver_lengths, 
			norm = matplotlib.colors.LogNorm(vmin=min(self.quiver_lengths), vmax=max(self.quiver_lengths), clip=True), 
			cmap='YlOrRd'
			)

		plt.scatter(self.charge_position[0], self.charge_position[1], color = 'blue')
		
		plt.axis([-10, 10, -10, 10])
		self.fig.canvas.draw()

class ContinuousPlotter(object):
	def __init__(self, get_next_frames_callback):
		self.get_next_frames_callback = get_next_frames_callback

		self.dt = 0.5
		self.frame_batch_duration = 10 * self.dt
		self.current_time = 0.0
		self.last_update_time = None
		self.update_period = self.frame_batch_duration

		assert(self.update_period <= self.frame_batch_duration)

		self.max_queue_size = 10

		self.frame_buffer_queue = queue.Queue( maxsize = self.max_queue_size )

		#need this to be atomic boolean (thread safe read/write)
		self.fetch_more_frames = AtomicVar(True)

	def fetch_continuously(self):
		frame_count = 0
		loop_count = 0
		while True:
			if not self.fetch_more_frames.getValue():
				#print ("don't need more frames")
				self.sleep_after_update()
				continue

			print("fetching because frame que has size", self.frame_buffer_queue.qsize())

			self.last_update_time = time.time()
			start_new_frame_callback = time.time()
			print ("fetching more frames")
			new_frames = self.get_next_frames_callback(self.dt, self.frame_batch_duration)
			finish_new_frame_callback = time.time()

			self.frame_buffer_queue.put(new_frames)
			self.sleep_after_update()


	def plot_continuously(self):
		self.scene = Scene()
		self.scene.initialize_view()
		frame_count = 0
		max_size = 0
		while True:
			buffer_queue_size = self.frame_buffer_queue.qsize()
			print ("buffer queue size", buffer_queue_size)
			self._check_need_for_frames()

			new_frames = self.frame_buffer_queue.get()
			for frame in new_frames:
				new_time, charge_position, field_samples = frame

				#sleep between rendering frames
				time.sleep((new_time - self.current_time) / fast_forward_rate)
				self.current_time = new_time

				self.scene.update_view(field_samples, charge_position)
				self.scene.plot_quivers()
		
	def _check_need_for_frames(self):
		buffer_queue_size = self.frame_buffer_queue.qsize()
		if buffer_queue_size >= self.max_queue_size * (9/10.0):
			self.fetch_more_frames.setValue(False)
		elif buffer_queue_size <= self.max_queue_size / 2:
			print ("need more frames")
			self.fetch_more_frames.setValue(True)

	def sleep_after_update(self):
		# no logic behind 0.1, just a hack
		time.sleep(0.1 * self.frame_buffer_queue.qsize() * self.update_period / fast_forward_rate)
		