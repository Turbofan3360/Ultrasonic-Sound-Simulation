#!/usr/bin/env python3

from math import sqrt, sin, pi, log10, exp
from multiprocessing import Pool
import matplotlib.pyplot as plt
import numpy as np

plotsize = 500 # Distance around the ultrasonic array that you're modelling (in centimeters)
cpu_cores = 6 # Number of CPU cores you want to use to run the simulation
# Locations of the transducers - formatted as [[x, y], [x, y]] in centimeters from origin
transducers = [[150, 250], [250, 250], [350, 250]]
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
	wave = 0

	for transducer in range(len(transducers)):
		# Calculating amplitude of a wave from a particular transducer at the point [x, y]
		wave_from_transducer, dist = distance_wavelengths(x, y, transducer)
		wave_sin = sin(wave_from_transducer*2*pi)

		# Calculating wave attenuation
		wave_attenuated = attenuate(wave_sin, dist)

		wave += wave_attenuated

	# Log-scaling the wave (converting it to dB)
	wave_scaled = log_scale(wave)

	return wave_scaled

def log_scale(amplitude):
	volume_db = 20*log10(abs(amplitude))

	return volume_db

def attenuate(wave_amplitude, dist):
	# dist in CM, needs converting to M
	dist /= 100

	wave_amplitude *= exp(-_attenuation_constant*dist) # Attenuation in air
	if dist: # Guarding against 0 divison error
		wave_amplitude /= dist # Attenuation due to distance (geometric)

	return wave_amplitude

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
	plt.imshow(data_matrix, cmap="plasma", interpolation="nearest", origin="lower")
	plt.colorbar()
	plt.title("Ultrasound Intensity Around A Transducer Array")
	plt.xlabel("Distance/CM")
	plt.ylabel("Distance/CM")

	plt.show()