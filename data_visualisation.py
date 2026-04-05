#!/usr/bin/env python3

import matplotlib.pyplot as plt
from simulation import runSimulation

# Class to plot interactive 3D heatmaps using matplotlib
class SoundSimPlot:
    data_matrix = []

    def _computeData():
        """
        Utility function to call compution of data
        """
        data = runSimulation()

    def plotSimulation2D():
        """
        Plots a 2-dimensional heatmap of the data using matplotlib
        """
        _computeData()

        # Handles plotting the simulation data in matplotlib
        cmap = plt.get_cmap("plasma").copy()
        cmap.set_under("lightgrey")
        plt.imshow(data_matrix, cmap=cmap, interpolation="bilinear", origin="lower", vmin=data_matrix.min(), vmax=data_matrix.min())
        plt.colorbar()

        if dBA:
            plt.title("Ultrasound Intensity (dBA) Around Transducer Array")
            else:
                plt.title("Ultrasound Intensity (dB) Around Transducer Array")

                plt.xlabel("Distance/MM")
                plt.ylabel("Distance/MM")

                plt.show()

    def plotSimulation3D():


if __name__ == "__main__":
    plotting = SoundSimPlot()
    plotting.plotSimulation2D()
