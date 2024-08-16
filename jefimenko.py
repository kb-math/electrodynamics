import math
import numpy as np
import time

import view.scene
from charge_sample import ChargeSample

class PointCharge(object):
    def __init__(self, position, charge_function, charge_rate_function):
        self.position = position
        self.charge_function = charge_function
        self.charge_rate_function = charge_rate_function

class ChargedRod(object):
    def __init__(self, start_charge, end_charge, current_rate_function):
        self.start_charge = start_charge
        self.end_charge = end_charge

        # quick reference
        start = self.start_charge.position
        end = self.end_charge.position

        # the current (in amps) moving uniformly from start to end direction
        self.current_rate_function = current_rate_function
        self.direction_unit_vector = (end - start)/np.linalg.norm(end - start)

        self.sampling_rate = 5

    #note: assuming speed of light = 1.0
    def calculate_electric_field(self, target, t):
        total_field = np.array([0.0, 0.0, 0.0])

        # quick reference
        start = self.start_charge.position
        end = self.end_charge.position

        distance_to_start = np.linalg.norm(target - start)
        distance_to_end = np.linalg.norm(target - end)

        charge_at_start = self.start_charge.charge_function(t - distance_to_start)
        charge_at_end = self.end_charge.charge_function(t - distance_to_end)

        total_field += charge_at_start * (target - start) / np.linalg.norm(target - start)**3
        total_field += charge_at_end * (target - end) / np.linalg.norm(target - end)**3

        charge_rate_at_start = self.start_charge.charge_rate_function(t - distance_to_start)
        charge_rate_at_end = self.end_charge.charge_rate_function(t - distance_to_end)

        total_field += charge_rate_at_start * (target - start) / np.linalg.norm(target - start)**2
        total_field += charge_rate_at_end * (target - end) / np.linalg.norm(target - end)**2

        segment_direction = (end - start) / float(self.sampling_rate * np.linalg.norm(start - end))
        segment_length = np.linalg.norm(segment_direction)

        integral_value = 0
        for i in range(self.sampling_rate + 1):
            sample_point = start + i * segment_direction
            distance_to_sample = np.linalg.norm(target - sample_point)

            integral_value -= 1/distance_to_sample * self.current_rate_function(t - distance_to_sample)

        total_field += integral_value * self.direction_unit_vector * segment_length

        return total_field


def create_periodic_charge_point(position, frequency, amplitude):
    charge_function = lambda t: amplitude * math.sin(2 * math.pi * frequency * t)
    charge_rate_function = lambda t: amplitude * 2 * math.pi * frequency * math.cos(2 * math.pi * frequency * t)

    return PointCharge(position, charge_function, charge_rate_function)

def create_charge_rod(start, end, frequency, amplitude):
    # note: the minus in front of amplitude is to guarantee the total charge is always 0
    start_charge = create_periodic_charge_point(start, frequency, -amplitude)
    end_charge = create_periodic_charge_point(end, frequency, amplitude)

    current_rate_function = lambda t: -amplitude * (2 * math.pi * frequency)**2 * math.sin(2 * math.pi * frequency * t)

    return ChargedRod(start_charge, end_charge, current_rate_function)

if __name__ == '__main__':
    charge_rod = create_charge_rod( np.array([0.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]), 0.1, 1.0)

    samples = []

    for i in range(-10, 10, 1):
        for j in range(-10, 10, 1):

            if (i,j) in [(1,0), (0,0)]:
                continue

            samples.append(np.array([float(i/1.0), float(j/1.0), 0.0]))

    viewer = view.scene.Scene()
    viewer.initialize_view()

    dt = 0.25
    current_time = 0.0
    while True:
        field_samples = []
        start_time = time.time()
        for sample in samples:
            field_samples.append((sample, charge_rod.calculate_electric_field(sample, current_time)))

        viewer.update_field_samples(field_samples)
        viewer.update_charge_samples( [
            ChargeSample(charge_rod.start_charge.position, charge_rod.start_charge.charge_function(current_time)),
            ChargeSample(charge_rod.end_charge.position, charge_rod.end_charge.charge_function(current_time))
            ] )

        end_time = time.time()
        time_to_sleep = max(0, dt - end_time + start_time)
        viewer.plot(time_to_sleep)

        current_time += dt





