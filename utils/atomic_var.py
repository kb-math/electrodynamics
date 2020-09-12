import threading

class AtomicVar(object):
	"""atomic read/write of a variable, implemented using locks"""
	def __init__(self, value):
		self._lock = threading.Lock()
		self._value = value

	def getValue(self):
		with self._lock:
			return self._value

	def setValue(self, new_value):
		if self._value != new_value:
			with self._lock:
				self._value = new_value
