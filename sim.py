#!/usr/bin/env python3

from math import sqrt, sin, pi, log10
from multiprocessing import Pool
import matplotlib.pyplot as plt
import numpy as np

plotsize = 500 # Distance around the ultrasonic array that you're modelling (in centimeters)
cpu_cores = 6 # Number of CPU cores you want to use to run the simulation
# Locations of the transducers - formatted as [[x, y], [x, y]] in centimeters from origin
#transducers = [[0, 8.6], [2.23, 8.31], [4.3, 7.45], [6.08, 6.08], [7.45, 4.3], [8.31, 2.23], [8.6, 0]]
transducers = [[100, 0], [200, 0], [300, 0]]
wavelength = 343/250 # in CM not M (250 as dividing by 25KHz, then multiplying by 100)

def log(string):
	print(string)

# Location is a list in form [x, y]
def distance_wavelengths(x, y, transducer_no):
	dist_sq = (x - transducers[transducer_no][0])**2 + (y - transducers[transducer_no][1])**2
	dist = sqrt(dist_sq)
	dist /= wavelength

	return dist

def sum_waves(x, y):
	wave = 0

	for transducer in range(len(transducers)):
		wave_from_transducer = distance_wavelengths(x, y, transducer)

		wave += sin(wave_from_transducer*2*pi)

	return wave

def log_scale(amplitude):
	volume_db = 20*log10(abs(amplitude))

	return volume_db

def generate_data_matrix_row(x):
	data_row = (plotsize+1)*[0]
	log("Processing row {}...".format(x))
	for y in range(plotsize+1):
		wave = sum_waves(x, y)
		wave_scaled = log_scale(wave)

		data_row[y] = wave_scaled

	return data_row


if __name__ == "__main__":
	x_values = list(range(plotsize+1))
	with Pool(processes=cpu_cores) as pool:
		data_matrix = pool.map(generate_data_matrix_row, x_values)

	data_matrix = np.array(data_matrix)

	# Configuring the heatmap plot to be how I like it
	plt.imshow(data_matrix, cmap="plasma", interpolation="nearest", origin="lower")
	plt.colorbar()
	plt.title("Ultrasound Intensity Around A Transducer Array")
	plt.xlabel("Distance/CM")
	plt.ylabel("Distance/CM")

	plt.show()