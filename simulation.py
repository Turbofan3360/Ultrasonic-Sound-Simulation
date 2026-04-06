#!/usr/bin/env python3

from math import sqrt, pi, log10, atan2, sin
from cmath import exp
from multiprocessing import Pool
import numpy as np
from SIM_CONFIG import *

# Wavelength in MM
_WAVELENGTH = (343/FREQUENCY)*1000
# Calculation using Stokes-Kirchoff Model, in Nepers/m
_ATTENUATION_CONSTANT = (2*1.85e-5*(2*pi*FREQUENCY)**2)/(3*1.225*(343**3))
# Used for calculating absolute volume of ultrasound at every point
_PRESS_AMPLITUDE = 0.00002 * (10**(TRANSDUCER_TRANSMITTING_PRESSURE_LEVEL/20))
_DEG_TO_RAD = pi/180
_TRANSDUCER_POS_VECTORS = [np.array(i[0]) for i in TRANSDUCERS]

def _logger(string):
    """
    Simple method to log a string to the screen.
    """
    print(string)

def _computeDBAWeight():
    """
    Calculates the adjustment value to convert from decibels to A-weighted decibels.

    Uses the standard calculation formula.
    """
    numerator = 148693636*FREQUENCY**4
    denominator = (FREQUENCY**2 + 20.6**2)*sqrt((FREQUENCY**2+107.7**2)*(FREQUENCY**2+737.9**2))
    denominator *= FREQUENCY**2+12194**2

    ra = numerator/denominator
    aweight = 20*log10(ra)+2

    return aweight

# TODO - this is ugly, move somewhere cleaner
_A_WEIGHT = _computeDBAWeight()

def _sinc(angle):
    """
    Maths function to calculate the value of the sinc of an angle.

    Output values is scaled based on the user-defined scalefactor.
    """
    # Input angle in radians
    x = pi*angle*SINC_SCALEFACTOR

    if x == 0:
        return 1

    return sin(x)/x

def _computeTransducerToPointAngle(x, y, transducer_no):
    """
    Calculates the angle between the transducer's central axis and specified point.

    Transducer's central axis defined in the TRANSDUCERS list.
    """
    dx = x - _TRANSDUCER_POS_VECTORS[transducer_no][0]
    dy = y - _TRANSDUCER_POS_VECTORS[transducer_no][1]

    angle_point = atan2(dy, dx)

    # Calculating angle delta between the transducer's direction and point
    angle = angle_point - (TRANSDUCERS[transducer_no][1]*_DEG_TO_RAD)

    # Constraining "angle" in range -pi -> +pi
    if angle > pi:
        angle -= 2*pi
    elif angle < -pi:
        angle += 2*pi

    return angle

def _computeAngleAttenuation(x, y, transducer_no):
    """
    Uses the transducer's central axis -> point angle, and the sinc function
    Determines the transducer's beam strength at the specified point

    If the central axis -> point angle is larger than the cutoff, 0 is returned
    """
    # Beam angle attenuation approximation using a sinc function + scaling it
    angle = _computeTransducerToPointAngle(x, y, transducer_no)

    # If angle>specified cutoff, then this just assumes 0 volume from transducer
    # Useful for simulating certain setups
    if abs(angle) > MAX_BEAM_ANGLE*_DEG_TO_RAD:
        return 0

    attenuation_factor = abs(_sinc(angle))

    return attenuation_factor

def _computeDistanceInWavelengths(x, y, transducer_no):
    """
    Calculates the absolute distance between the transducer and specified point
    Also calculates the distance in wavelengths of sound that is being modelled
    """
    point_vec = np.array([x, y])
    vec = np.subtract(point_vec, _TRANSDUCER_POS_VECTORS[transducer_no])
    dist = np.linalg.norm(vec)

    dist_lambdas = dist/_WAVELENGTH

    return dist_lambdas, dist

def _sumWavesAtPoint(x, y):
    """
    Calculates phasors for each transducer's wave, sums them together to get the resultant wave.
    Takes into account atmospheric/geometric/beam angle attenuation.

    Output is in decibels/A-weighted decibels, depending on user configuration.
    """
    wave = 0 + 0j

    for transducer in range(len(TRANSDUCERS)):
        # Calculating phase offset of wave from a particular transducer
        phase_offset, dist = _computeDistanceInWavelengths(x, y, transducer)
        phase_offset *= 2*pi
        phase_offset += TRANSDUCERS[transducer][2]

        # Calculating wave attenuation due to distance/atmospheric absorbtion
        # Then converting that to an absolute pressure amplitude
        amplitude = _PRESS_AMPLITUDE * R0 * _computeDistanceAttenuation(dist)

        # Calculating the strength of the ultrasound beam from the transducer at this point
        angle_attenuation = _computeAngleAttenuation(x, y, transducer)

        # Calculating phasor
        complex_phase = complex(0, phase_offset)
        wave_calc = amplitude*angle_attenuation*exp(complex_phase)

        # Summing phasors
        wave += wave_calc

    # Converting wave sum to dB/dBA, depending on user configuration
    wave_scaled = _convertToDb(abs(wave))

    return wave_scaled

def _convertToDb(amplitude):
    """
    Scales wave amplitude (in Pa) into a decibel volume reading.
    """
    if amplitude:
        volume_db = 20*log10(amplitude/0.00002)
    else:
        return 0

    if dBA:
        volume_db += _A_WEIGHT

    return volume_db

def _computeDistanceAttenuation(dist):
    """
    Calculates the wave's attenutation - both due to geometric and atmospheric attenuation.
    """
	# dist in mm, needs converting to m
    dist /= 1000

    # Attenuation in air
    amplitude = exp(-_ATTENUATION_CONSTANT*dist)

    # Guarding against 0 divison error
    if dist:
        # Attenuation due to distance
        amplitude /= dist

    return amplitude

def _generateDataRow(y):
    """
    Function to handle the generation of data for each row of the data matrix.
    """
    data_row = (PLOTSIZE+1)*[0]
    _logger("Processing row {}...".format(y))

    for x in range(PLOTSIZE+1):
        wave = _sumWavesAtPoint(x, y)

        data_row[x] = wave

    return data_row

def runSimulation2D():
    """
    Handles running the sound simulation (across multiple CPU cores)
    Returns the data as a numpy matrix array
    """
    y_values = list(range(PLOTSIZE+1))
    with Pool(processes=CPU_CORES) as pool:
        data_matrix = pool.map(_generateDataRow, y_values)

    data_matrix_np = np.array(data_matrix)

    return data_matrix_np
