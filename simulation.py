from lienard_wiechert import *
import kinematics.motion_lib as motion_lib
from view.scene import *

import math
import numpy as np
import time

dt = 0.8

# radiation that has travelled further than this won't be plotted to save CPU and RAM
MAX_DISTANCE = 15.0


class FieldTail(object):
	def __init__(self, position, source_position, source_velocity, source_acceleration):
		self._position = np.array(position)
		self._source_position = np.array(source_position)
		self._source_velocity = np.array(source_velocity)
		self._source_acceleration = np.array(source_acceleration)
		self._time = np.linalg.norm(source_position - position)/SPEED_OF_LIGHT
		self._direction = (position - source_position)/np.linalg.norm(source_position - position)

	def advance(self, dt):
		self._time += dt
		self._position += self._direction * dt * SPEED_OF_LIGHT

	def E_vector(self):
		return electric_field(self._source_position, self._source_velocity, self._source_acceleration, self._position)


if __name__ == '__main__':
	
	points_unit_circle = []

	for k in range(8):
		theta = 2*math.pi*k/8
		points_unit_circle.append(np.array([math.cos(theta), math.sin(theta), 0]))

	field_view = Scene()
	field_view.initialize_view()

	charge_motion = motion_lib.Sinusoidal(freq = 0.1, max_speed = 0.6 * SPEED_OF_LIGHT)
	'''
	charge_motion = motion_lib.ConstantAcc(
		np.array([0.1,0.0,0.0]), 
		np.array([-0.9,0.0,0.0]), 
		np.array([0.0,0.0,0.0]))
	'''
	field_tails = []

	current_time = 0.0
	br = 0

	#TODO: factor in general speed of light and consequent retardation
	while (True):
		charge_kinematics = charge_motion.get_state(current_time)
		charge_position = np.array(charge_kinematics.position)
		charge_velocity = np.array(charge_kinematics.velocity)
		charge_acceleration = np.array(charge_kinematics.acceleration)

		for unit_point in points_unit_circle:
			field_tails.append(FieldTail(unit_point + charge_position, charge_position, charge_velocity, charge_acceleration))

		late_index = None
		curr_index = 0

		field_view.update_view(field_tails, charge_position)
		
		for field_tail in field_tails:
			field_tail.advance(dt)

			# we need to delete the first few tails as they are too old, they are ordered chronologically
			# by creation time. These old are so far you can't see them so don't process them to save
			# CPU and RAM
			if field_tail._time > MAX_DISTANCE / SPEED_OF_LIGHT:
				late_index = curr_index
			curr_index += 1

		if late_index is not None:
			#TODO: field_tails should be a deque and we can pop
			del field_tails[:late_index]

		field_view.plot_quivers()

		br += 1
		current_time += dt
		time.sleep(dt * 0.2)

