### ALL THE CONFIGURABLE VARIABLES IN THE SIMULATION ARE HERE ###
### Configure these variables to set up your simulation ###

import numpy as np

# Distance around the ultrasonic array that you're modelling (in millimeters)
PLOTSIZE = 500
# Sife length of the cells in the simulation, in mm
CELL_SIDE_LENGTH_MM = 1
# 2D or 3D simulation
sim3D = True
# Adjusts how 3D data is displayed
# 0 -> 2D slices through the volume, 1 -> Full 3D visualisation of the data
VIEWMODE_3D = 1
# If True, the program uses Float32/Complex64 instead of Float64/Complex 128 for reduced memory usage
COMPRESS_FLOAT = True
# Max. number of CPU cores to be used in running the simulation
CPU_CORES = 6
# Simulated sound frequency in Hz
FREQUENCY = 25000
# Comes from transducer datasheet, in dB
TRANSDUCER_TRANSMITTING_PRESSURE_LEVEL = 120
# The distance at which transducer's transmitting sound pressure level is measured, in M
R0 = 0.3
# Boolean to determine whether you want the output as dBA (True) or dB (False)
dBA = True
# Transducer data formatted as [[x-y position vector], [x-y transducer central axis vector], phase offset (radians)]]
# Vectors are in terms of mm from the origin (NOT simulation cells from the origin)
# Vectors should always be x-y-z, even if running a 2D simulation. Set z=0 in vectors when wanting a 2D simulation
TRANSDUCERS = [
    [[150, 50, 0], [0, 1, 0], 0],
    [[250, 50, 0], [0, 1, 0], 0],
    [[350, 50, 0], [0, 1, 0], 0]
]

# Scale factor to make the sinc function behave as wanted for beam angle attenuation
SINC_SCALEFACTOR = 1.15
# In radians - the angle from the transducer's axis to the edge of its beam
MAX_BEAM_ANGLE = 100*(np.pi/180)

def userComputeBeamAngleResponse(angles_matrix):
    """
    Computes scalars for every point in the grid to apply the transducer's beam angle profile
    User-definable - all operations here should be NumPy matrix operations, suggested to be in float32/complex64 for memory efficiency

    The angles_matrix parameter is a matrix of the angle of each point in the
    plot from the transducer's central axis (in radians)

    Currently applies a sinc() approximation of a beam angle profile, with a cutoff angle
    """
    sinc_args = np.multiply(angles_matrix, np.pi*SINC_SCALEFACTOR)

    # Keeping values in range for sinc() function
    sinc_args = np.where(sinc_args == 0, 1, sinc_args)

    # Applying the scaled sinc function to each of the points in the matrix
    beam_angle_scalars = np.where(
        np.abs(angles_matrix) > MAX_BEAM_ANGLE,
        0,
        np.abs(np.sin(sinc_args) / sinc_args)
    )

    return beam_angle_scalars
