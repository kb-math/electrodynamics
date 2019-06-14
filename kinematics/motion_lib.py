import math
import numpy as np

class KinematicsState(object):
	def __init__(self, position, velocity, acceleration):
		self.position = np.array(position)
		self.velocity = np.array(velocity)
		self.acceleration = np.array(acceleration)

class Motion(object):
	def __init__(self, pos_func, vel_func, acc_func):
		self._pos = pos_func
		self._vel = vel_func
		self._acc = acc_func

	def get_state(self, t):
		return KinematicsState(self._pos(t), self._vel(t), self._acc(t))

# Examples

def ConstantAcc(a, u, pos0):
	return Motion(
			lambda t: 0.5*a * t**2 + u*t + pos0, 
			lambda t: a*t + u, 
			lambda t: a)

def Sinusoidal(freq, max_speed, pos0 = np.array([0.0, 0.0, 0.0]), direction = np.array([1.0,0.0,0.0])):
	omega = 2*math.pi*freq
	direction /= np.linalg.norm(direction)
	amplitude = max_speed/omega * direction
	return Motion(
			lambda t: amplitude * math.sin(omega*t) + pos0,
			lambda t: amplitude * omega * math.cos(t),
			lambda t: -amplitude**2 * omega * math.sin(t))
