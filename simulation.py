from lienard_wiechert import *
import kinematics.motion_lib as motion_lib

import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time

dt = 0.8

# how many metres represents one newton per coulomb
ELECTRIC_FIELD_SCALING = 0.1

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

	ax = plt.axes()
	fig = plt.figure()
	fig.show()

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
		plt.clf()
		charge_kinematics = charge_motion.get_state(current_time)
		charge_position = np.array(charge_kinematics.position)
		charge_velocity = np.array(charge_kinematics.velocity)
		charge_acceleration = np.array(charge_kinematics.acceleration)

		for unit_point in points_unit_circle:
			field_tails.append(FieldTail(unit_point + charge_position, charge_position, charge_velocity, charge_acceleration))

		quiver_base_x_list = []
		quiver_base_y_list = []
		quiver_x_list = []
		quiver_y_list = []
		quiver_lengths = []

		late_index = None
		curr_index = 0
		for field_tail in field_tails:
			E_vector = field_tail.E_vector()
			E_vector *= ELECTRIC_FIELD_SCALING
			E_vector_length = np.linalg.norm(E_vector)
			x = np.array(field_tail._position)

			quiver_base_x_list.append(x[0])
			quiver_base_y_list.append(x[1])
			#scale the vector a unit vector otherwise creetes clutter
			quiver_x_list.append(E_vector[0] if E_vector_length == 0.0 else E_vector[0] / E_vector_length)
			quiver_y_list.append(E_vector[1] if E_vector_length == 0.0 else E_vector[1] / E_vector_length)
			quiver_lengths.append(E_vector_length)

			#TODO: be careful of sneaky python pass by reference?
			field_tail.advance(dt)

			# we need to delete the first few tails as they are too old, they are ordered chronologically
			# by creation time. These old are so far you can't see them so don't process them to save
			# CPU and RAM
			if field_tail._time > MAX_DISTANCE / SPEED_OF_LIGHT:
				late_index = curr_index
			curr_index += 1

		if late_index is not None:
			del field_tails[:late_index]

		plt.quiver(quiver_base_x_list, quiver_base_y_list, quiver_x_list, quiver_y_list, 
			quiver_lengths, 
			norm = matplotlib.colors.LogNorm(vmin=min(quiver_lengths), vmax=max(quiver_lengths), clip=True), 
			cmap='Greys')
		plt.scatter(charge_position[0], charge_position[1], color = 'blue')
		
		plt.axis([-10, 10, -10, 10])
		fig.canvas.draw()

		br += 1
		current_time += dt
		time.sleep(dt * 0.2)

