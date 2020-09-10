import lienard_wiechert
from lienard_wiechert import SPEED_OF_LIGHT as SPEED_OF_LIGHT
import kinematics.motion_lib as motion_lib
from view.scene import *

import argparse
import math
import numpy as np
import time

# radiation that has travelled further than this won't be plotted to save CPU and RAM
MAX_DISTANCE = 15.0

electric_field_function = None

fast_forward_rate = 5.0

class ElectricFieldSample(object):
	def __init__(self, direction, source_position, source_velocity, source_acceleration):
		self._direction = np.array(direction)
		self._position = np.array(source_position)
		self._source_position = np.array(source_position)
		self._source_velocity = np.array(source_velocity)
		self._source_acceleration = np.array(source_acceleration)
		self._time = 0
		self.E_vector = None

	def advance(self, dt):
		self._time += dt
		self._position += self._direction * dt * SPEED_OF_LIGHT
		self.update_electric_field()

	def update_electric_field(self):
		self.E_vector = electric_field_function(
			self._source_position, self._source_velocity, self._source_acceleration, self._position)

	def too_old(self):
		return self._time * SPEED_OF_LIGHT > MAX_DISTANCE

class SimulationEngine(object):
	def __init__(self, charge_motion, direction_unit_vectors):
		self._charge_motion = charge_motion
		#directions that field samples move in
		self._direction_unit_vectors = direction_unit_vectors

		self._current_time = 0.0
		self._last_sample_generation_time = None
		self._sample_generation_period = 0.0
		self._field_samples = []

		self._update_charge_kinematics()

	def _update_charge_kinematics(self):
		charge_kinematics = self._charge_motion.get_state(self._current_time)

		self._charge_position = np.array(charge_kinematics.position)
		self._charge_velocity = np.array(charge_kinematics.velocity)
		self._charge_acceleration = np.array(charge_kinematics.acceleration)

	def _emit_new_field_samples(self):
		for unit_vec in self._direction_unit_vectors:
			self._field_samples.append(ElectricFieldSample(unit_vec, self._charge_position, 
				self._charge_velocity, self._charge_acceleration))

	def advance_simulation(self, dt):
		#emit new samples from the old charge position, we must do this before updating the position
		if (self._last_sample_generation_time is None) or (self._current_time > self._last_sample_generation_time + self._sample_generation_period): 
			self._emit_new_field_samples()
			self._last_sample_generation_time = self._current_time

		self._current_time += dt
		self._update_charge_kinematics()

		late_index = None
		
		for curr_index, field_sample in enumerate(self._field_samples):

			# we need to delete the last few samples as they are too old, they are ordered chronologically
			# by creation time. These old are so far you can't see them so don't process them to save
			# CPU and RAM
			if field_sample.too_old():
				late_index = curr_index
				continue

			field_sample.advance(dt)

		if late_index is not None:
			#TODO: self._field_samples should be a deque and we can pop
			del self._field_samples[:late_index]

	def get_next_frames(self, dt, frame_count):
		pass

	@property
	def field_samples(self):
		return self._field_samples

	@property
	def charge_position(self):
		return self._charge_position

	@property
	def current_time(self):
		return self._current_time

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--far', default = False, action = 'store_true', 
		help = "only plot far field component")
	args = parser.parse_args()

	electric_field_function = lienard_wiechert.electric_field
	if args.far:
		electric_field_function = lienard_wiechert.far_field_term
	points_unit_circle = []

	for k in range(8):
		theta = 2*math.pi*k/8
		points_unit_circle.append(np.array([math.cos(theta), math.sin(theta), 0]))

	field_view = Scene()
	field_view.initialize_view()

	charge_motion = motion_lib.Sinusoidal(freq = 0.05, max_speed = 0.9 * SPEED_OF_LIGHT)
	'''
	charge_motion = motion_lib.ConstantAcc(
		np.array([0.1,0.0,0.0]), 
		np.array([-0.9,0.0,0.0]), 
		np.array([0.0,0.0,0.0]))
	'''

	simulation_engine = SimulationEngine(charge_motion, direction_unit_vectors = points_unit_circle)
	dt = 0.5

	#TODO: factor in general speed of light and consequent retardation
	while (True):

		simulation_engine.advance_simulation(dt)

		field_view.update_view(simulation_engine.field_samples, simulation_engine.charge_position)
		field_view.plot_quivers()

		time.sleep(dt/fast_forward_rate)
