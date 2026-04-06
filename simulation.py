#!/usr/bin/env python3

from cmath import exp
from multiprocessing import Pool
import numpy as np
from SIM_CONFIG import *

# Wavelength in MM
_WAVELENGTH = (343/FREQUENCY)*1000
# Calculation using Stokes-Kirchoff Model, in Nepers/m
_ATTENUATION_CONSTANT = (2*1.85e-5*(2*np.pi*FREQUENCY)**2)/(3*1.225*(343**3))
# Used for calculating absolute volume of ultrasound at every point
_PRESS_AMPLITUDE = 0.00002 * (10**(TRANSDUCER_TRANSMITTING_PRESSURE_LEVEL/20))
_DEG_TO_RAD = np.pi/180
_TRANSDUCER_POS_VECTORS = [np.array(i[0]) for i in TRANSDUCERS]
_TRANSDUCER_AXIS_VECTORS = [np.array(i[1]) for i in TRANSDUCERS]

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
    denominator = (FREQUENCY**2 + 20.6**2)*np.sqrt((FREQUENCY**2+107.7**2)*(FREQUENCY**2+737.9**2))
    denominator *= FREQUENCY**2+12194**2

    ra = numerator/denominator
    aweight = 20*np.log10(ra)+2

    return aweight

def _computeBeamAngleFactors(angles_matrix):
    """
    Computes scalars for every point in the grid to apply the transducer's beam angle profile
    Currently uses a sinc function approximation, this can be changed
    """
    sinc_args = np.multiply(angles_matrix, np.pi*SINC_SCALEFACTOR)

    # Keeping values in range for sinc() function
    sinc_args = np.where(sinc_args == 0, 1, sinc_args)

    # Applying the scaled sinc function to each of the points in the matrix
    beam_angle_scalars = np.where(
        np.abs(angles_matrix) > MAX_BEAM_ANGLE*_DEG_TO_RAD,
        0,
        np.abs(np.sin(sinc_args) / sinc_args)
    )

    return beam_angle_scalars

def _computeAttenuationFactor(dist_matrix):
    """
    Calculates and applies attenuation to the amplitude matrix
    Takes into account distance/atmospheric attenuation as well as due to the transducer beam profile
    """
    # Converting from mm to m, can be adapted depending on desired sim resolution
    dist_matrix = np.divide(dist_matrix, 1000)

    # Calculating atmospheric attenuation of sound
    atmospheric_attenuation = np.multiply(dist_matrix, -_ATTENUATION_CONSTANT)
    atmospheric_attenuation = np.exp(atmospheric_attenuation)

    # Calculating attenuation of sound due to distance
    # Guards against zero division error
    safe_distances = np.where(
        dist_matrix == 0,
        1,
        dist_matrix
    )
    attenuated = np.where(
        dist_matrix == 0,
        0,
        np.divide(atmospheric_attenuation, safe_distances)
    )

    return attenuated

def _computeTransducerDistancesAngles(transducer_pos, transducer_axis):
    """
    Computes a matrix of the distances between the transducer and each point in the grid
    Computes a matrix of the angles between the transducer central axis and each point in the grid
    """
    transducer_x, transducer_y = transducer_pos

    # Shaping my x/y values into matrices of the right shape
    x_vals = np.array(range(PLOTSIZE+1)).reshape(1, PLOTSIZE+1)
    y_vals = np.array(range(PLOTSIZE+1)).reshape(PLOTSIZE+1, 1)

    # Calculating the x/y deltas between the transducer position and each point in the grid
    delta_x_vals = x_vals - transducer_x
    delta_y_vals = y_vals - transducer_y

    # Combining to calculate distances
    distance_sq = np.square(delta_x_vals) + np.square(delta_y_vals)
    distances = np.sqrt(distance_sq)

    # Calculating dot product matrix
    dot_product_matrix = delta_x_vals*transducer_axis[0] + delta_y_vals*transducer_axis[1]

    axis_vec_length = np.linalg.norm(transducer_axis)

    # Calculating the cosine of the angles as a matrix
    angles_cosine = np.divide(dot_product_matrix, axis_vec_length)
    # Guarding against zero-division errors
    # IDEA: Only modify transducer position cell in distances, as that's the only one == 0
    safe_distances = np.where(distances == 0, 1, distances)
    angles_cosine = np.divide(angles_cosine, safe_distances)
    # Keeping cosine values in range
    angles_cosine = np.clip(angles_cosine, -1, 1)

    # Calculating the angles as a matrix
    angles = np.arccos(angles_cosine)

    return distances, angles

def _generateTransducerMatrix(transducer_no):
    """
    Generates a matrix showing the volumes produced due to the single transducer at each point in the grid
    """
    # Creating an initial uniform sound amplitude matrix
    amplitude_matrix = np.full(
        (PLOTSIZE+1, PLOTSIZE+1),
        _PRESS_AMPLITUDE * R0
    )

    # Computing all required bits to determine sound wave amplitude at each point in the grid
    # Then applying these to the amplitude matrix
    dist_matrix, angle_matrix = _computeTransducerDistancesAngles(
        _TRANSDUCER_POS_VECTORS[transducer_no],
        _TRANSDUCER_AXIS_VECTORS[transducer_no]
    )
    attenuation_factors = _computeAttenuationFactor(dist_matrix)
    beam_angle_factors = _computeBeamAngleFactors(angle_matrix)

    amplitude_matrix = np.multiply(amplitude_matrix, attenuation_factors)
    amplitude_matrix = np.multiply(amplitude_matrix, beam_angle_factors)

    # Computing phase offset in radians at each point in the grid
    dist_matrix_wavelength = np.divide(dist_matrix, _WAVELENGTH)
    dist_matrix_wavelength = np.multiply(dist_matrix_wavelength, 2*np.pi)
    # Adding on transducer phase offset
    dist_matrix_wavelength = np.add(dist_matrix_wavelength, TRANSDUCERS[transducer_no][2])

    # Using those to calculate (absolute) amplitude scalars
    wave_phase_cosine = np.cos(dist_matrix_wavelength)

    # Applying wave phase scalars to the wave amplitude at each point in the grid
    amplitude_matrix = np.multiply(amplitude_matrix, wave_phase_cosine)

    return amplitude_matrix

def runVectorisedSimulation2D():
    """
    Runs the simulation as a fully vectorised operation.

    For each transducer, a matrix is computed with the volume levels at each
    point in the simulation grid, and these matrices are then added together.
    """
    transducer_indexes = list(range(len(TRANSDUCERS)))

    # If user wants results in dBA, need to compute the weighting for it
    dba_weight = _computeDBAWeight()

    with Pool(processes=CPU_CORES) as pool:
        results = pool.map(_generateTransducerMatrix, transducer_indexes)

    # Summing all my results matrices
    sim_matrix = np.sum(results, axis=0)
    sim_matrix = np.abs(sim_matrix)

    # Producing a safe matrix to then logarithmically scale to dB
    sim_matrix_safe = np.where(
        sim_matrix == 0,
        0.00002,
        sim_matrix
    )

    # Computing the volume in dB from the amplitude matrix
    sim_matrix_db = 20*np.log10(sim_matrix_safe/0.00002) + dba_weight

    # Removing sub-zero values
    sim_matrix_db = np.where(
        sim_matrix_db < 0,
        0,
        sim_matrix_db
    )

    return sim_matrix_db
