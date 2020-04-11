import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# how many metres represents one newton per coulomb
ELECTRIC_FIELD_SCALING = 0.1

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

	def update_view(self, field_tails, charge_position):
		self.charge_position = charge_position

		self.quiver_base_x_list = []
		self.quiver_base_y_list = []
		self.quiver_x_list = []
		self.quiver_y_list = []
		self.quiver_lengths = []

		for field_tail in field_tails:
			E_vector = field_tail.E_vector()
			E_vector *= ELECTRIC_FIELD_SCALING
			E_vector_length = np.linalg.norm(E_vector)

			self.quiver_base_x_list.append(field_tail._position[0])
			self.quiver_base_y_list.append(field_tail._position[1])
			#scale the vector a unit vector otherwise creetes clutter
			self.quiver_x_list.append(E_vector[0] if E_vector_length == 0.0 else E_vector[0] / E_vector_length)
			self.quiver_y_list.append(E_vector[1] if E_vector_length == 0.0 else E_vector[1] / E_vector_length)
			self.quiver_lengths.append(E_vector_length)

	def plot_quivers(self):
		plt.clf()
		plt.quiver(self.quiver_base_x_list, self.quiver_base_y_list, self.quiver_x_list, self.quiver_y_list, 
		self.quiver_lengths, 
		norm = matplotlib.colors.LogNorm(vmin=min(self.quiver_lengths), vmax=max(self.quiver_lengths), clip=True), 
		cmap='Greys')

		plt.scatter(self.charge_position[0], self.charge_position[1], color = 'blue')
		
		plt.axis([-10, 10, -10, 10])
		self.fig.canvas.draw()
		