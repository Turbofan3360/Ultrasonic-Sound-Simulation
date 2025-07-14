# Ultrasonic Microphone Jammer Simulation #

### Source and Idea: ### 

This is based on a project from the University of Chicago's SAND Lab (Project page: <https://sandlab.cs.uchicago.edu/jammer/>). The aim of the project was to create a wearable jammer
that uses ultrasonic sound to jam many common microphones (e.g. used in Alexa/Google Home voice assistants, mobile phones, e.t.c.).

I decided to try and use their idea to create a stationary ultrasonic jammer. The key issue with a stationary jammer is the potential blind spots, which aren't 'blurred out' by movement
(as a wearable jammer gets moved randomly). To solve this, I need to work out an approach that uses multiple signal drivers, rather than just one, to try and remove blind spots. However,
I needed to simulate this in order to come up with a valid solution - hence this piece of code.

_More details about their project and simulation (page 5 of the paper) in their paper, written here: <https://people.cs.uchicago.edu/~ravenben/publications/pdf/ultra-chi20.pdf>_

### The Code: ###

This simulation sums up the waves at every point in the user-defined grid size (using phasors, i.e. Euler's formula), using the path difference of the waves from each ultrasonic
transducer (considered a point source currently), and then log-scales that to a decibel result for that square. The program also takes into account signal attenuation (both over
distance and in air). This is a parallelised program, so you will also need to define the number of CPU cores that the program can utilize.

In future, I will be adding:
 - Transducers that are no longer point sources
 - Hopefully much more!

### Variables: ###

For you to run the program, you will need to define a few variables:

plotsize (line 9): This defines the side length of the square plot produced by the simulation in milimeters

cpu_cores (line 10): This defines the number of CPU cores that the program will use when simulating

transducers (line 15): This defines the location of the transducers as a list of [x, y, phase offset] co-ordinate lists (co-ordinates in milimeters from the origin). You can also set
a phase offset (in radians) for the transducer in the 3rd element of the list.

frequency (line 11): This defines the frequency of ultrasound you want to simulate. Currently, this is set to 25 KHz.

transducer_transmitting_sound_pressure_level (line 12): This value (from your transducer datasheet, in dB) is used to calculate the absolute volume of ultrasound at the points in the heatmap,
rather than just calculating the ultrasound volume relative to the transducer.
