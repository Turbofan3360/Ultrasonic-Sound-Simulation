#!/usr/bin/env python3

import matplotlib.pyplot as plt
from simulation import runVectorisedSimulation2D, runVectorisedSimulation3D
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

    def _updateXYSlice(self, val):
        """
        Updates the XY slice of the heatmap data being visualizes
        """
        self.im1.set_data(self.data_matrix[val])
        plt.draw()

    def plotSimulation2D(self):
        """
        Plots a 2-dimensional heatmap of the data using matplotlib
        """
        self.data_matrix = runVectorisedSimulation2D()

        # Creates a standardised colour map for the heatmaps
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

        plt.gcf().canvas.manager.set_window_title("Sound Simulation")

        plt.show()

    def plotSimulation3D(self):
        """
        Plots a 3-dimensional heatmap of the data
        Plus a slider to let you select which volumes to show
        """
        self.data_matrix = runVectorisedSimulation3D()

        # Creates a set of subplots to plot on
        fig, axes = plt.subplots(1, 1)
        fig.canvas.manager.set_window_title("Sound Simulation")

        # Creates a standardised colour map for the heatmaps
        cmap = plt.get_cmap("plasma").copy()
        cmap.set_under("lightgrey")

        self.im1 = axes.imshow(self.data_matrix[0],
            cmap=cmap,
            interpolation="bilinear",
            origin="lower",
            vmin=self._computeMatrixNonZeroMin(self.data_matrix),
            vmax=self.data_matrix.max()
        )
        fig.colorbar(im1, ax=axes, orientation='vertical', fraction=0.05)

        if dBA:
            axes.set_title("Ultrasound Intensity (dBA) Around Transducer Array")
        else:
            axes.set_title("Ultrasound Intensity (dB) Around Transducer Array")

        plt.xlabel("Distance/MM")
        plt.ylabel("Distance/MM")

        # Adding a slider to control which XY slice is shown in the heatmap
        axamp = fig.add_axes([0.1, 0.25, 0.0225, 0.63])
        xy_slice_slider = Slider(
            ax = axamp,
            label ="XY Slice Z-Height",
            valmin=0,
            valmax=PLOTSIZE,
            valinit=0,
            orientation="vertical"
        )
        xy_slice_slider.on_changed(self._updateXYSlice)

        plt.show()


if __name__ == "__main__":
    plotting = SoundSimPlot()

    if sim3D:
        plotting.plotSimulation3D()
    else:
        plotting.plotSimulation2D()
