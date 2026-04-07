# Ultrasonic Sound Simulation #

### The Idea: ###

This is based on a project from the University of Chicago's SAND Lab (Project page: <https://sandlab.cs.uchicago.edu/jammer/>). The aim of the project was to create a wearable jammer that uses ultrasonic sound to jam many common microphones (e.g. used in Alexa/Google Home voice assistants, mobile phones, e.t.c.).

I wanted to write a simulation which could replicate the simulation results achieved in their paper.

_More details about their project and simulation in their paper, written here: <https://people.cs.uchicago.edu/~ravenben/publications/pdf/ultra-chi20.pdf>_

![Example image - 9 transducers, planar arrangment, no phase offsets](images/1_signal_9_transducers_planar.png)
![Example image - 24 transducers, ring arrangement, no phase offsets](images/1_signal_24_transducers_ring.png)

### The Code: ###

This simulation is a fully vectorised (using NumPy) computation that computes a matrix of the wave from each transducer across the grid. These matrices are then summed together, before the resulting wave magnitude at each point is taken to determine the final simulation result. Results are log-scaled that to a decibel result - either dB or dBA, depending on the your preference.

The computation of the wave matrix from each transducer is run in parallel - one CPU core per transducer.

Any ideas to improve the simulation quality are welcome!

### Simulation Configuration: ###

In the SIM_CONFIG.py file are all the things that can be tuned to produce your simulation.

PLOTSIZE - The size of each side of the plot (in millimeters - to reduce simulation resolution requires a bit more code tweaking)
CPU_CORES - The maximum number of CPU cores the simulation will use when running
FREQUENCY - The sound frequency, in Hz, being simulated
TRANSDUCER_TRANSMITTING_PRESSURE_LEVEL - The volume of your transducer, in dB
R0 - The distance at which TRANSDUCER_TRANSMITTING_PRESSURE_LEVEL is measured, in meters
dBA - Whether or not the simulation output is in dB (dBA = False) or dBA (dBA = True)
TRANSDUCERS - An array describing your transducer setup. Each transducer should be formatted as: [[x-y position vector], [x-y central axis vector], phase offset (radians)]

User-defined function userComputeBeamAngleResponse(angle_matrix):

This is where you can write your own function which the simulation will use to describe how the transducer's emitted sound amplitude varies with angle from the transducer central axis. Currently, this is a simple sinc() function approximation. When writing your own function here, ensure all the operations are NumPy matrix operations for efficiency and execution speed.
