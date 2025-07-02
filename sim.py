#!/usr/bin/env python3

from math import sqrt, pi, log10
from cmath import exp
from multiprocessing import Pool
import matplotlib.pyplot as plt
import numpy as np

plotsize = 100 # Distance around the ultrasonic array that you're modelling (in centimeters)
cpu_cores = 6 # Number of CPU cores you want to use to run the simulation
# Locations of the transducers - formatted as [[x, y], [x, y]] in centimeters from origin
transducers = [[0, 8.6], [2.23, 8.31], [4.3, 7.45], [6.08, 6.08], [7.45, 4.3], [8.31, 2.23], [8.6, 0]]
frequency = 250000 # in Hz

_wavelength = (343/frequency)*100 # in CM not M
_attenuation_constant = (2*1.85e-5*(2*pi*frequency)**2)/(3*1.225*(343**3)) # Calculation using Stokes-Kirchoff Model, in Nepers/m

def log(string):
	print(string)

# Location is a list in form [x, y]
def distance_wavelengths(x, y, transducer_no):
	dist_sq = (x - transducers[transducer_no][0])**2 + (y - transducers[transducer_no][1])**2
	dist = sqrt(dist_sq)
	dist_lambdas = dist/_wavelength

	return dist_lambdas, dist

def sum_waves(x, y):
	wave = 0 + 0j

	for transducer in range(len(transducers)):
		# Calculating phase offset of a wave from a particular transducer at the point [x, y]
		phase_offset, dist = distance_wavelengths(x, y, transducer)
		phase_offset *= 2*pi

		# Calculating wave attenuation
		amplitude = attenuate(dist)

		# Calculating phasor
		complex_phase = complex(0, phase_offset)
		wave_calc = amplitude*exp(complex_phase)

		# Summing phasors
		wave += wave_calc

	# Log-scaling (converting to dB) the modulus of the phasor sum wave
	wave_scaled = log_scale(abs(wave))

	return wave_scaled

def log_scale(amplitude):
	if amplitude:
		volume_db = 20*log10(amplitude)
	else:
		# volume_db would actually go to −∞, but can't represent that. -200 is low enough
		return -200
	return volume_db

def attenuate(dist):
	# dist in CM, needs converting to M
	dist /= 100

	amplitude = exp(-_attenuation_constant*dist) # Attenuation in air
	if dist: # Guarding against 0 divison error
		amplitude /= dist # Attenuation due to distance (geometric)

	return amplitude

def generate_data_matrix_row(y):
	data_row = (plotsize+1)*[0]
	log("Processing row {}...".format(y))
	
	for x in range(plotsize+1):
		wave = sum_waves(x, y)

		data_row[x] = wave

	return data_row


if __name__ == "__main__":
	y_values = list(range(plotsize+1))
	with Pool(processes=cpu_cores) as pool:
		data_matrix = pool.map(generate_data_matrix_row, y_values)

	data_matrix = np.array(data_matrix)

	# Configuring the heatmap plot to be how I like it
	if plotsize >= 250:
		interpolation_value = "bilinear"
	else:
		interpolation_value = "nearest"

	plt.imshow(data_matrix, cmap="plasma", interpolation=interpolation_value, origin="lower")
	plt.colorbar()
	plt.title("Ultrasound Intensity Around Transducer Array")
	plt.xlabel("Distance/CM")
	plt.ylabel("Distance/CM")

	plt.show()