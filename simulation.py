from lienard_wiechert import *

import math
import numpy as np
import matplotlib.pyplot as plt
import time

# how many metres represents one newton per coulomb
ELECTRIC_FIELD_SCALING = 0.6

class FieldTail(object):
	def __init__(self, position, source_position, source_velocity, source_acceleration):
		self._position = position
		self._source_position = source_position
		self._source_velocity = source_velocity
		self._source_acceleration = source_acceleration
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

	charge_position = np.array([0.0, 0.0, 0.0])
	charge_velocity = np.array([0.0, 0.0, 0.0])
	charge_acceleration = np.array([5.0, 0.0, 0.0])

	field_tails = []

	radius = 1.0
	dt_loop = 0.5

	current_time = dt_loop

	#TODO: factor in general speed of light and consequent retardation
	while (True):
		plt.clf()
		for unit_point in points_unit_circle:
			field_tails.append(FieldTail(unit_point, charge_position, charge_velocity, charge_acceleration))

		for field_tail in field_tails:
			E_vector = field_tail.E_vector()
			E_vector *= ELECTRIC_FIELD_SCALING
			E_vector_length = np.linalg.norm(E_vector)
			x = np.array(field_tail._position)
			plt.arrow(x[0], x[1], E_vector[0], E_vector[1], head_width = 0.5, head_length = 0.5)

			#TODO: be careful of sneaky python pass by reference?

			field_tail.advance(dt_loop)

			#TODO: if we run this forever, we should probably clear points too far apart (should be ordered)
			#solution: flag the index of a field_tail really close to boundary and delete all after that index

		plt.axis([-10, 10, -10, 10])
		fig.canvas.draw()

		#radius += dt_loop * SPEED_OF_LIGHT

		time.sleep(dt_loop)
