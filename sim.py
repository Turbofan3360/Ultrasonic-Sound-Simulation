#!/usr/bin/env python3

from math import sqrt, pi, log10
from cmath import exp
from multiprocessing import Pool
import matplotlib.pyplot as plt
import numpy as np

plotsize = 1000 # Distance around the ultrasonic array that you're modelling (in milimeters)
cpu_cores = 6 # Number of CPU cores you want to use to run the simulation
# Locations of the transducers - formatted as [[x, y, phase offset], [x, y, phase offset]] in milimeters from origin and phase offset in radians (i.e. range of 0 -> 2*pi)
transducers = [
	[500, 586, 0], [522.3, 583.1, pi/12], [543, 574.5, (2/12)*pi], [560.8, 560.8, (3/12)*pi], [574.5, 543, (4/12)*pi], [583.1, 522.3, (5/12)*pi],
	[586, 500, (6/12)*pi], [583.1, 477.7, (7/12)*pi], [574.5, 457, (8/12)*pi], [560.8, 439.2, (9/12)*pi], [543, 425.5, (10/12)*pi], [522.3, 416.9, (11/12)*pi],
	[500, 414, pi], [477.7, 416.9, (13/12)*pi], [457, 425.5, (14/12)*pi], [439.2, 439.2, (15/12)*pi], [425.5, 457, (16/12)*pi], [416.9, 477.7, (17/12)*pi],
	[414, 500, (18/12)*pi], [416.9, 522.3, (19/12)*pi], [425.5, 543, (20/12)*pi], [439.2, 560.8, (21/12)*pi], [457, 574.5, (22/12)*pi], [477.7, 583.1, (23/12)*pi]
	]
#transducers = [
#	[500, 586, 0], [522.3, 583.1, pi/3], [543, 574.5, (2/3)*pi], [560.8, 560.8, pi], [574.5, 543, (4/3)*pi], [583.1, 522.3, (5/3)*pi],
#	[586, 500, 0], [583.1, 477.7, pi/3], [574.5, 457, (2/3)*pi], [560.8, 439.2, pi], [543, 425.5, (4/3)*pi], [522.3, 416.9, (5/3)*pi],
#	[500, 414, 0], [477.7, 416.9, pi/3], [457, 425.5, (2/3)*pi], [439.2, 439.2, pi], [425.5, 457, (4/3)*pi], [416.9, 477.7, (5/3)*pi],
#	[414, 500, 0], [416.9, 522.3, pi/3], [425.5, 543, (2/3)*pi], [439.2, 560.8, pi], [457, 574.5, (4/3)*pi], [477.7, 583.1, (5/3)*pi]
#	]
frequency = 25000 # in Hz

_wavelength = (343/frequency)*1000 # in MM not M
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
		phase_offset += transducers[transducer][2]

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
	# dist in MM, needs converting to M
	dist /= 1000

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

	plt.imshow(data_matrix, cmap="plasma", interpolation="bilinear", origin="lower")
	plt.colorbar()
	plt.title("Ultrasound Intensity (dB) Around Transducer Array")
	plt.xlabel("Distance/MM")
	plt.ylabel("Distance/MM")

	plt.show()
frequency = 25000 # in Hz

_wavelength = (343/frequency)*1000 # in MM not M
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
		phase_offset += transducers[transducer][2]

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
	# dist in MM, needs converting to M
	dist /= 1000

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

	plt.imshow(data_matrix, cmap="plasma", interpolation="bilinear", origin="lower")
	plt.colorbar()
	plt.title("Ultrasound Intensity (dB) Around Transducer Array")
	plt.xlabel("Distance/MM")
	plt.ylabel("Distance/MM")

	plt.show()