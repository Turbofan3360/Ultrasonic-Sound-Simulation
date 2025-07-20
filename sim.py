#!/usr/bin/env python3

## TODO: FIX HOW ABSOLUTE VOLUMES ARE HANDLED SO ULTRASOUND VOLUME CLOSE TO TRANSDUCER == TRANSMITTING SOUND PRESSURE LEVEL

from math import sqrt, pi, log10, atan2, sin
from cmath import exp
from multiprocessing import Pool
import matplotlib.pyplot as plt
import numpy as np

plotsize = 1000 # Distance around the ultrasonic array that you're modelling (in milimeters)
cpu_cores = 6 # Number of CPU cores you want to use to run the simulation
frequency = 25000 # in Hz
transducer_transmitting_sound_pressure_level = 120 # in dB
transducer_radius = 8 # in mm
max_beam_angle = 100 # in degrees - the angle from the transducer's axis to the edge of its beam
sinc_scalefactor = 1.38 # scale factor I figured out to make my sinc function behave as I want for beam angle attenuation (~-6dB at 25 degrees)

# Locations of the transducers - formatted as [[x, y, angle (degrees), phase offset], [x, y, angle (degrees), phase offset]] in milimeters from origin and phase offset in radians (i.e. range of 0 -> 2*pi)
transducers = [
    [500, 586, 90, 0], [522.3, 583.1, 75,pi/3], [543, 574.5, 60, (2/3)*pi], [560.8, 560.8, 45, pi], [574.5, 543, 30, (4/3)*pi], [583.1, 522.3, 15, (5/3)*pi],
    [586, 500, 0, 0], [583.1, 477.7, -15, pi/3], [574.5, 457, -30, (2/3)*pi], [560.8, 439.2, -45, pi], [543, 425.5, -60, (4/3)*pi], [522.3, 416.9, -75, (5/3)*pi],
    [500, 414, -90, 0], [477.7, 416.9, -105, pi/3], [457, 425.5, -120, (2/3)*pi], [439.2, 439.2, -135, pi], [425.5, 457, -150, (4/3)*pi], [416.9, 477.7, -165, (5/3)*pi],
    [414, 500, -180, 0], [416.9, 522.3, 165, pi/3], [425.5, 543, 150, (2/3)*pi], [439.2, 560.8, 135, pi], [457, 574.5, 120, (4/3)*pi], [477.7, 583.1, 105, (5/3)*pi]
     ]
#transducers = [[500, 500, 180, 0]]

_wavelength = (343/frequency)*1000 # in MM not M
_attenuation_constant = (2*1.85e-5*(2*pi*frequency)**2)/(3*1.225*(343**3)) # Calculation using Stokes-Kirchoff Model, in Nepers/m
_press_amplitude = 0.00002 * (10**(transducer_transmitting_sound_pressure_level/20)) # used for calculating absolute volume of ultrasound at every point
_degto_rad = pi/180

def log(string):
    print(string)

def sinc(angle): # angle in radians
    x = pi*angle*sinc_scalefactor

    if x == 0:
        return 1

    return sin(x)/x

def angle_between_point_transducer(x, y, transducer_no):
    dx = x - transducers[transducer_no][0]
    dy = y - transducers[transducer_no][1]

    angle_point = atan2(dy, dx) # Calculates the angle (in range +pi -> -pi radians) between the point you're 

    angle = angle_point - (transducers[transducer_no][2]*_degto_rad) # Calculating the angle delta between the transducer's direction and the point (in radians)

    if angle > pi:
        angle -= 2*pi
    elif angle < -pi:
        angle += 2*pi

    return angle

def beam_angle_attenuation(x, y, transducer_no):
    ### THIS IS AN APPROXIMATION USING A SINC FUNCTION AND SCALING IT (AS NO EXACT DATA IS AVAILABLE FOR THE TCT25-16T TRANSDUCER)
    angle = angle_between_point_transducer(x, y, transducer_no)

    if abs(angle) > max_beam_angle*_degto_rad: # For my situation, I'm considering the ring of transducers to be mounted in a solid box (as will be the case when I build this for real). As a result, at angles > 100 degrees, I consider the transducer to have no effect.
        return 0

    attenuation_factor = abs(sinc(angle))

    return attenuation_factor

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
        phase_offset += transducers[transducer][3]

        # Calculating wave attenuation due to distance
        amplitude = _press_amplitude * attenuate(dist)

        # Calculating the strength of the ultrasound beam from the transducer at this point
        angle_attenuation = beam_angle_attenuation(x, y, transducer)

        # Calculating phasor
        complex_phase = complex(0, phase_offset)
        wave_calc = amplitude*angle_attenuation*exp(complex_phase)

        # Summing phasors
        wave += wave_calc

    # Log-scaling (converting to dB) the modulus of the phasor sum wave
    wave_scaled = log_scale(abs(wave))

    return wave_scaled

def log_scale(amplitude):
    if amplitude:
        volume_db = 20*log10(amplitude/0.00002)
    else:
        # volume_db would actually go to −∞, but can't represent that. -200 is low enough
        return 0
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

#    data = [beam_angle_attenuation(i*(pi/180)) for i in range(180)]
#    angles = np.arange(len(data))  # 0°, 1°, 2°, ..., 89°

 #   plt.figure(figsize=(8, 4))
  #  plt.plot(angles, data, marker='o')
   # plt.title("Beam Attenuation vs Angle")
    #plt.xlabel("Angle (degrees)")
    #plt.ylabel("Amplitude Attenuation")
    #plt.grid(True)
    #plt.show()