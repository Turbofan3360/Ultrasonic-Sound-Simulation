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

# Transducer data formatted as [[x (mm), y (mm ), angle (degrees), phase offset (radians)], ...]
TRANSDUCERS = [
    [500, 586, 90, 0], [522.3, 583.1, 75,0], [543, 574.5, 60, 0], [560.8, 560.8, 45, 0], [574.5, 543, 30, 0], [583.1, 522.3, 15, 0],
    [586, 500, 0, 0], [583.1, 477.7, -15, 0], [574.5, 457, -30, 0], [560.8, 439.2, -45, 0], [543, 425.5, -60, 0], [522.3, 416.9, -75, 0],
    [500, 414, -90, 0], [477.7, 416.9, -105, 0], [457, 425.5, -120, 0], [439.2, 439.2, -135, 0], [425.5, 457, -150, 0], [416.9, 477.7, -165, 0],
    [414, 500, -180, 0], [416.9, 522.3, 165, 0], [425.5, 543, 150, 0], [439.2, 560.8, 135, 0], [457, 574.5, 120, 0], [477.7, 583.1, 105, 0]
     ]
