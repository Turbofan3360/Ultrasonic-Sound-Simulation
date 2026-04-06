#!/usr/bin/env python3

import matplotlib.pyplot as plt
from simulation import runSimulation2D
from SIM_CONFIG import *

# Class to plot interactive 3D heatmaps using matplotlib
class SoundSimPlot:
    data_matrix = []

    def _computeMatrixNonZeroMin(self, data):
        """
        Finds the minimum value in a 2-dimensional list.

        Ignores values that are 0, as they are blanked out in the heatmap
        """
        # Higher than the max. theoretical pressure level
        current_min = (len(TRANSDUCERS)+1)*TRANSDUCER_TRANSMITTING_PRESSURE_LEVEL
        for a in range(len(data)):
            for b in range(len(data[a])):
                if data[a][b] < current_min and data[a][b] != 0:
                    current_min = data[a][b]

        return current_min

    def plotSimulation2D(self):
        """
        Plots a 2-dimensional heatmap of the data using matplotlib
        """
        self.data_matrix = runSimulation2D()

        # Handles plotting the simulation data in matplotlib
        cmap = plt.get_cmap("plasma").copy()
        cmap.set_under("lightgrey")
        plt.imshow(self.data_matrix,
            cmap=cmap,
            interpolation="bilinear",
            origin="lower",
            vmin=self._computeMatrixNonZeroMin(self.data_matrix),
            vmax=self.data_matrix.max()
        )
        plt.colorbar()

        if dBA:
            plt.title("Ultrasound Intensity (dBA) Around Transducer Array")
        else:
            plt.title("Ultrasound Intensity (dB) Around Transducer Array")

            plt.xlabel("Distance/MM")
            plt.ylabel("Distance/MM")

        plt.show()

    def plotSimulation3D(self):
        """
        Plots a 3-dimensional heatmap of the data
        Plus a slider to let you select which volumes to show
        """
        pass


if __name__ == "__main__":
    plotting = SoundSimPlot()
    plotting.plotSimulation2D()
