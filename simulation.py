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

class FieldTail(object):
	def __init__(self, position, source_position, source_velocity, source_acceleration):
		self._position = np.array(position)
		self._source_position = np.array(source_position)
		self._source_velocity = np.array(source_velocity)
		self._source_acceleration = np.array(source_acceleration)
		self._time = np.linalg.norm(source_position - position)/SPEED_OF_LIGHT
		self._direction = (position - source_position)/np.linalg.norm(source_position - position)
		self.E_vector = None

		self.update_electric_field()

	def advance(self, dt):
		self._time += dt
		self._position += self._direction * dt * SPEED_OF_LIGHT
		self.update_electric_field()

	def update_electric_field(self):
		self.E_vector = electric_field_function(
			self._source_position, self._source_velocity, self._source_acceleration, self._position)

class SimulationEngine(object):
	def __init__(self, electric_field_function, charge_motion, direction_unit_vectors, field_view = None):
		self._charge_motion = charge_motion
		self._electric_field_function = electric_field_function
		self._direction_unit_vectors = direction_unit_vectors

		self._current_time = 0.0
		self._field_tails = []

		#TODO: remove these
		self._field_view = field_view

	def advance_simulation(self, dt):
		charge_kinematics = self._charge_motion.get_state(self._current_time)
		charge_position = np.array(charge_kinematics.position)
		charge_velocity = np.array(charge_kinematics.velocity)
		charge_acceleration = np.array(charge_kinematics.acceleration)

		for unit_vec in points_unit_circle:
			self._field_tails.append(FieldTail(charge_position + unit_vec, charge_position, 
				charge_velocity, charge_acceleration))

		late_index = None
		curr_index = 0

		field_view.update_view(self._field_tails, charge_position)
		
		for field_tail in self._field_tails:
			field_tail.advance(dt)

			# we need to delete the first few tails as they are too old, they are ordered chronologically
			# by creation time. These old are so far you can't see them so don't process them to save
			# CPU and RAM
			if field_tail._time > MAX_DISTANCE / SPEED_OF_LIGHT:
				late_index = curr_index
			curr_index += 1

		if late_index is not None:
			#TODO: self._field_tails should be a deque and we can pop
			del self._field_tails[:late_index]

		field_view.plot_quivers()

		self._current_time += dt

	def get_next_frames(self, dt, frame_count):
		pass


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

	simulation_engine = SimulationEngine(electric_field_function, charge_motion, points_unit_circle, 
		field_view = field_view)
	dt = 0.5

	#TODO: factor in general speed of light and consequent retardation
	while (True):
		simulation_engine.advance_simulation(dt)
		time.sleep(dt * 0.2)

