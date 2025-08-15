# Ultrasonic Microphone Jammer Simulation #

### Source and Idea: ### 

This is based on a project from the University of Chicago's SAND Lab (Project page: <https://sandlab.cs.uchicago.edu/jammer/>). The aim of the project was to create a wearable jammer that uses ultrasonic sound to jam many common microphones (e.g. used in Alexa/Google Home voice assistants, mobile phones, e.t.c.).

I decided to try and use their idea to create a stationary ultrasonic jammer. The key issue with a stationary jammer is the potential blind spots, which aren't 'blurred out' by movement (as a wearable jammer gets moved randomly). To solve this, I need to work out an approach that uses multiple signal drivers, rather than just one, to try and remove blind spots. However, I needed to simulate this in order to come up with a valid solution - hence this piece of code.

_More details about their project and simulation (page 5 of the paper) in their paper, written here: <https://people.cs.uchicago.edu/~ravenben/publications/pdf/ultra-chi20.pdf>_

_This code still doesn't precisely resemble the simulations in the paper above (although it is a reasonably accurate simulation). My goal is to learn more of the maths and physics used in the paper's simulation, and then use that to update my code._

![Example image - 9 transducers, planar arrangment, no phase offsets](~/images/1_signal_9_transducers_planar.png)
![Example image - 24 transducers, ring arrangement, no phase offsets](~/images/1_signal_24_transducers_ring.png)

### The Code: ###

This simulation sums up the waves at every point in the user-defined grid size (using phasors, i.e. Euler's formula), using the path difference of the waves from each ultrasonic transducer, and then log-scales that to a decibel result for that square. The decibel value is the absolute ultrasound volume at that point. The program takes into account signal attenuation (both over distance and in atmosphere). This is a parallelised program, so you will also need to define the number of CPU cores that the program can utilize.

The code simulates the transducers' beam angle plots as a sinc function, which I tuned to what I thought it should be for the TCT25-16T transducer I intend to use - there was no precise beam angle plot available. The sinc function was based on the one datapoint I had: the attenuation is -6dB @ 25 degrees from the transducer's axis. This will need to be adjusted for other transducers - it's all in the sinc() function.

Any ideas to improve the simulation quality are welcome!

### Variables: ###

For you to run the program, you will need to define a few variables:

_plotsize (line 9):_ This defines the side length of the square plot produced by the simulation in millimeters (mm)

_cpu_cores (line 10):_ This defines the number of CPU cores that the program will use when simulating

_frequency (line 11):_ This defines the frequency of ultrasound you want to simulate in Hz. Currently, this is set to 25 KHz.

_transducer_transmitting_sound_pressure_level (line 12):_ This value (from your transducer datasheet, in dB) is used to calculate the absolute volume of ultrasound at the points in the heatmap, rather than just calculating the ultrasound volume relative to the transducer.

_r0 (line 13):_ This is the distance at which the transducer_transmitting_sound_pressure_level is defined at (in meters)

_max_beam_angle (line 14):_ This determines the angle from the transducer's central axis to the edge of its beam (in degrees). Set to 180 to have a full beam.

_sinc_scalefact (line 15):_ This is used to calculate the beam angle plot - for more details see "The Code" above. This will need to be tuned for different kinds of transducers (currently suited for the TCT25-16T)

_dBA (line 16):_ If set to True, the output heatmap will be in dBA. If set to False, the output heatmap will be left in dB

_transducers (line 15):_ This defines the location of the transducers as a list of [x, y, axis angle, phase offset] co-ordinate lists (co-ordinates in millimeters from the origin). The axis angle is the direction in which the transducer is pointing - measured in degrees above the positive x-axis (range -180 --> 180 degrees). You can also set a phase offset (in radians) for the transducer in the 3rd element of the list.