### ALL THE CONFIGURABLE VARIABLES IN THE SIMULATION ARE HERE ###
### Configure these variables to set up your simulation ###

# Distance around the ultrasonic array that you're modelling (in millimeters)
PLOTSIZE = 500
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

# Transducer data formatted as [x-y position vector], [x-y transducer axis vector], phase offset (radians)]
TRANSDUCERS = [
    [[150, 50], [0, 1], 0],
    [[250, 50], [0, 1], 0],
    [[350, 50], [0, 1], 0]
]
