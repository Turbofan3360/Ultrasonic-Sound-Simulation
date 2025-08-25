#!/usr/bin/env python3

from math import sqrt, pi, log10, atan2, sin
from cmath import exp
from multiprocessing import Pool
import matplotlib.pyplot as plt
import numpy as np

# Distance around the ultrasonic array that you're modelling (in millimeters)
PLOTSIZE = 2000
# Number of CPU cores you want to use to run the simulation
CPU_CORES = 6
# Simulated sound frequency in Hz
FREQUENCY = 25000 
# Comes from transducer datasheet, in dB
TRANSDUCER_TRANSMITTING_PRESSURE_LEVEL = 120
# The distance at which transducer's transmitting sound pressure level is measured, in M
R0 = 0.3
# In degrees - the angle from the transducer's axis to the edge of its beam
MAX_BEAM_ANGLE = 100
# Scale factor to make the sinc function behave as wanted for beam angle attenuation
SINC_SCALEFACTOR = 1.15
# Boolean to determine whether you want the output as dBA (True) or dB (False)
dBA = True

# Transducer data - formatted as [[x (mm from origin), y (mm from origin), angle (degrees), phase offset (radians)], ...]
transducers = [
    [500, 586, 90, 0], [522.3, 583.1, 75,0], [543, 574.5, 60, 0], [560.8, 560.8, 45, 0], [574.5, 543, 30, 0], [583.1, 522.3, 15, 0],
    [586, 500, 0, 0], [583.1, 477.7, -15, 0], [574.5, 457, -30, 0], [560.8, 439.2, -45, 0], [543, 425.5, -60, 0], [522.3, 416.9, -75, 0],
    [500, 414, -90, 0], [477.7, 416.9, -105, 0], [457, 425.5, -120, 0], [439.2, 439.2, -135, 0], [425.5, 457, -150, 0], [416.9, 477.7, -165, 0],
    [414, 500, -180, 0], [416.9, 522.3, 165, 0], [425.5, 543, 150, 0], [439.2, 560.8, 135, 0], [457, 574.5, 120, 0], [477.7, 583.1, 105, 0]
     ]

# Wavelength in MM
_WAVELENGTH = (343/FREQUENCY)*1000
# Calculation using Stokes-Kirchoff Model, in Nepers/m
_ATTENUATION_CONSTANT = (2*1.85e-5*(2*pi*FREQUENCY)**2)/(3*1.225*(343**3))
# Used for calculating absolute volume of ultrasound at every point
_PRESS_AMPLITUDE = 0.00002 * (10**(TRANSDUCER_TRANSMITTING_PRESSURE_LEVEL/20))
_DEG_TO_RAD = pi/180

def log(string):
    print(string)

def dba_weight():
    numerator = 148693636*FREQUENCY**4
    denominator = (FREQUENCY**2 + 20.6**2)*sqrt((FREQUENCY**2+107.7**2)*(FREQUENCY**2+737.9**2))*(FREQUENCY**2+12194**2)

    Ra = numerator/denominator
    aweight = 20*log10(Ra)+2

    return aweight

def sinc(angle):
    # Input angle in radians
    x = pi*angle*SINC_SCALEFACTOR

    if x == 0:
        return 1

    return sin(x)/x

def angle_transducer_to_point(x, y, transducer_no):
    dx = x - transducers[transducer_no][0]
    dy = y - transducers[transducer_no][1]

    angle_point = atan2(dy, dx)

    # Calculating the angle delta between the transducer's direction and the point (in radians)
    angle = angle_point - (transducers[transducer_no][2]*_DEG_TO_RAD)

    if angle > pi:
        angle -= 2*pi
    elif angle < -pi:
        angle += 2*pi

    return angle

def beam_angle_attenuation(x, y, transducer_no):
    # This is a beam angle attenuation approximation using a sinc() function, and scaling it
    angle = angle_transducer_to_point(x, y, transducer_no)

    # If angle > specified cutoff, then this just assumes 0 volume from transducer
    # Useful for simulating certain setups
    if abs(angle) > MAX_BEAM_ANGLE*_DEG_TO_RAD:
        return 0

    attenuation_factor = abs(sinc(angle))

    return attenuation_factor

# Location is a list in form [x, y]
def distance_wavelengths(x, y, transducer_no):
    dist_sq = (x - transducers[transducer_no][0])**2 + (y - transducers[transducer_no][1])**2
    dist = sqrt(dist_sq)
    dist_lambdas = dist/_WAVELENGTH

    return dist_lambdas, dist

def sum_waves(x, y):
    wave = 0 + 0j

    for transducer in range(len(transducers)):
        # Calculating phase offset of wave from a particular transducer
        phase_offset, dist = distance_wavelengths(x, y, transducer)
        phase_offset *= 2*pi
        phase_offset += transducers[transducer][3]

        # Calculating wave attenuation due to distance/atmospheric absorbtion
        # Then converting that to an absolute pressure amplitude
        amplitude = _PRESS_AMPLITUDE * R0 * attenuate(dist)

        # Calculating the strength of the ultrasound beam from the transducer at this point
        angle_attenuation = beam_angle_attenuation(x, y, transducer)

        # Calculating phasor
        complex_phase = complex(0, phase_offset)
        wave_calc = amplitude*angle_attenuation*exp(complex_phase)

        # Summing phasors
        wave += wave_calc

    # Log-scaling (converting to dB) the modulus of the sum of the waves
    wave_scaled = log_scale(abs(wave))

    return wave_scaled

def log_scale(amplitude):
    if amplitude:
        volume_db = 20*log10(amplitude/0.00002)
    else:
        return 0

    if dBA:
        volume_db += _A_WEIGHT

    return volume_db

def attenuate(dist):
	# dist in MM, needs converting to M
	dist /= 1000

    # Attenuation in air
	amplitude = exp(-_ATTENUATION_CONSTANT*dist)

    # Guarding against 0 divison error
	if dist:
        # Attenuation due to distance
		amplitude /= dist

	return amplitude

def generate_data_matrix_row(y):
	data_row = (PLOTSIZE+1)*[0]
	log("Processing row {}...".format(y))
	
	for x in range(PLOTSIZE+1):
		wave = sum_waves(x, y)

		data_row[x] = wave

	return data_row

def matrix_min_max(data):
    # Finds the minimum value in a list of lists 
    # Ignores values that are 0, as they are blanked out in the heatmap

    current_min = (len(transducers)+1)*TRANSDUCER_TRANSMITTING_PRESSURE_LEVEL
    current_max = 0
    for a in range(len(data)):
        for b in range(len(data[a])):
            if data[a][b] < current_min and data[a][b] != 0:
                current_min = data[a][b]
            if data[a][b] > current_max:
                current_max = data[a][b]

    return current_min, current_max

if __name__ == "__main__":
    if dBA:
        # Calculating the weighting if user wants result to be in dBA
        _A_WEIGHT = dba_weight()


    y_values = list(range(PLOTSIZE+1))
    with Pool(processes=CPU_CORES) as pool:
        data_matrix = pool.map(generate_data_matrix_row, y_values)

    data_matrix = np.array(data_matrix)
    data_min, data_max = matrix_min_max(data_matrix)
    cmap = plt.get_cmap("plasma").copy()
    cmap.set_under("lightgrey")
    plt.imshow(data_matrix, cmap=cmap, interpolation="bilinear", origin="lower", vmin=data_min, vmax=data_max)
    plt.colorbar()

    if dBA:
        plt.title("Ultrasound Intensity (dBA) Around Transducer Array")
    else:
        plt.title("Ultrasound Intensity (dB) Around Transducer Array")
    
    plt.xlabel("Distance/MM")
    plt.ylabel("Distance/MM")

    plt.show()
