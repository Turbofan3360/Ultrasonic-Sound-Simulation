# Ultrasonic Microphone Jammer Simulation #

### Source and Idea: ### 

This is based on a project from the University of Chicago's SAND Lab (Project page: <https://sandlab.cs.uchicago.edu/jammer/>). The aim of the project was to create a wearable jammer
that uses ultrasonic sound to jam many common microphones (e.g. used in Alexa/Google Home voice assistants, mobile phones, e.t.c.).

I decided to try and use their idea to create a stationary ultrasonic jammer. The key issue with a stationary jammer is the potential blind spots, which aren't 'blurred out' by movement
(as a wearable jammer gets moved randomly). To solve this, I need to work out an approach that uses multiple signal drivers, rather than just one, to try and remove blind spots. However,
I needed to simulate this in order to come up with a valid solution - hence this piece of code.

_More details about their project and simulation (page 5 of the paper) in their paper, written here: <https://people.cs.uchicago.edu/~ravenben/publications/pdf/ultra-chi20.pdf>_

### The Code: ###

Currently, this is a very basic simulation. Fundamentally, it just sums up the waves at every point in the user-defined grid size, using the path difference of the waves from each
ultrasonic transducer (considered a point source currently), and then log-scales that to a decibel result for that square. This is a parallelised program, so you will also need to
define the number of CPU cores that the program can utilize.

In future, I will be adding:
 - Signal attenuation over distance
 - Ring arrays with a phase difference between each transducer
 - Transducers that are no longer point sources
 - Hopefully much more!

### Variables: ###

For you to run the program, you will need to define a few variables:

plotsize (line 8): This defines the side length of the square plot produced by the simulation

cpu_cores (line 9): This defines the number of CPU cores that the program will use when simulating

transducers (line 11): This defines the location of the transducers as a list of [x, y] co-ordinate lists.

wavelength (line 12): This defines the frequency/wavelength of sound you are simulating (in cm, as that is the standard I am using across the simulation). This DOES NOT have to be
changed. Currently it is set to 25KHz.