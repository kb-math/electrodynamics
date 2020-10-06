from simulation_engine import *
from utils.flask_helper import *

from flask import Flask, json
from flask import request

class SimulationServer(object):
	def __init__(self, simulation_engine):
		self.simulation_engine = simulation_engine
		self.server = Flask(__name__)

		@self.server.route('/trajectory', methods=['GET'])
		@crossdomain(origin='*')
		def get_trajectories():
			duration = float(request.args.get("duration"))
			dt = float(request.args.get("dt"))

			result = self.simulation_engine.multistep_advance(dt, duration)

			return json.dumps(result)

	def start_server(self):
		self.server.run()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--far', default = False, action = 'store_true', 
		help = "only plot far field component")
	args = parser.parse_args()

	electric_field_function = lienard_wiechert.electric_field
	if args.far:
		electric_field_function = lienard_wiechert.far_field_term
	points_unit_circle = []

	ElectricFieldSample.set_electric_field_function(electric_field_function)

	for k in range(8):
		theta = 2*math.pi*k/8
		points_unit_circle.append(np.array([math.cos(theta), math.sin(theta), 0]))


	charge_motion = motion_lib.Sinusoidal(freq = 0.05, max_speed = 0.9 * SPEED_OF_LIGHT)
	'''
	charge_motion = motion_lib.ConstantAcc(
		np.array([0.1,0.0,0.0]), 
		np.array([-0.9,0.0,0.0]), 
		np.array([0.0,0.0,0.0]))
	'''

	simulation_engine = SimulationEngine(charge_motion, direction_unit_vectors = points_unit_circle)

	simulation_server = SimulationServer(simulation_engine)
	simulation_server.start_server()

