import math
import numpy as np

#source: 
# https://en.wikipedia.org/wiki/Li%C3%A9nard%E2%80%93Wiechert_potential#Corresponding_values_of_electric_and_magnetic_fields

SPEED_OF_LIGHT = 1.0

def near_field_term(source_position, source_velocity, target_position):
	displacement = target_position - source_position
	distance = np.linalg.norm(displacement)
	displacement_normalised = displacement / distance
	normalised_velocity = source_velocity / SPEED_OF_LIGHT

	lorentz_factor_squared = 1 / (1 - normalised_velocity)

	scaling = (lorentz_factor_squared * (1 - displacement_normalised.dot(normalised_velocity))**3)

	return (displacement_normalised - normalised_velocity) / (scaling * distance**2)

#TODO: optimization, use values calculated in near_field_term
def far_field_term(source_position, source_velocity, source_acceleration, target_position):
	displacement = target_position - source_position
	distance = np.linalg.norm(displacement)
	displacement_normalised = displacement / distance
	normalised_velocity = source_velocity / SPEED_OF_LIGHT

	normalised_acceleration = source_acceleration / SPEED_OF_LIGHT

	cross1 = np.cross(displacement_normalised - normalised_velocity, normalised_acceleration)
	numerator = np.cross(displacement_normalised, cross1)

	scaling = SPEED_OF_LIGHT * (1 - displacement_normalised.dot(normalised_velocity))**3

	denominator = SPEED_OF_LIGHT * scaling * distance

	return numerator/denominator

def electric_field(source_position, source_velocity, source_acceleration, target_position):
	near_field = near_field_term(source_position, source_velocity, target_position)
	far_field = far_field_term(source_position, source_velocity, source_acceleration, target_position)

	return near_field + far_field
