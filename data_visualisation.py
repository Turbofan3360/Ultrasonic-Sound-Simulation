#!/usr/bin/env python3

from matplotlib.widgets import Slider
import matplotlib.pyplot as plt
from simulation import runVectorisedSimulation2D, runVectorisedSimulation3D
from SIM_CONFIG import *

# Class to plot interactive 3D heatmaps using matplotlib
class SoundSimPlot:
    data_matrix = []

    def _compute2DMatrixNonZeroMin(self, data):
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
        self.im1.set_data(self.data_matrix[:, :, val])
        plt.draw()

    def _updateYZSlice(self, val):
        """
        Updates the YZ slice of the heatmap data being visualizes
        """
        self.im2.set_data(self.data_matrix[:, val, :])
        plt.draw()

    def _updateXZSlice(self, val):
        """
        Updates the XZ slice of the heatmap data being visualizes
        """
        self.im3.set_data(self.data_matrix[val, :, :])
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
            vmin=self._compute2DMatrixNonZeroMin(self.data_matrix),
            vmax=self.data_matrix.max()
        )
        plt.colorbar()

        plt.title(f"Ultrasound Intensity {"(dBA)" if dBA else "(dB)"}")

        plt.xlabel("Distance/MM")
        plt.ylabel("Distance/MM")

        plt.gcf().canvas.manager.set_window_title("Sound Simulation")

        plt.show()

    def plotSimulation3D(self):
        """
        Plots a 3-dimensional heatmap of the data
        Plus sliders to let you slice through cross-sections of the data
        """
        self.data_matrix = np.load("sim_data.npy")

        # Creates a set of subplots to plot on
        fig, axes = plt.subplots(1, 3)
        fig.canvas.manager.set_window_title("Sound Simulation")

        # Creates a standardised colour map for the heatmaps
        cmap = plt.get_cmap("plasma").copy()
        cmap.set_under("lightgrey")

        # TODO: Proper minimum value calculation
        self.im1 = axes[0].imshow(self.data_matrix[:, :, 0],
            cmap=cmap,
            interpolation="bilinear",
            origin="lower",
            vmin=0.1,
            vmax=self.data_matrix.max()
        )
        self.im2 = axes[1].imshow(self.data_matrix[:, 0, :],
            cmap=cmap,
            interpolation="bilinear",
            origin="lower",
            vmin=0.1,
            vmax=self.data_matrix.max()
        )
        self.im3 = axes[2].imshow(self.data_matrix[0, :, :],
            cmap=cmap,
            interpolation="bilinear",
            origin="lower",
            vmin=0.1,
            vmax=self.data_matrix.max()
        )

        fig.colorbar(self.im3, ax=axes[2], orientation='vertical', fraction=0.05)

        #axes[0].set_title(f"Ultrasound Intensity {"(dBA)" if dBA else "(dB)"}")

        plt.xlabel("Distance/MM")
        plt.ylabel("Distance/MM")

        # Adding sliders to control which slices are shown in the heatmaps
        sl_axes_1 = fig.add_axes([0.1, 0.2, 0.025, 0.6])
        xy_slice_slider = Slider(
            ax = sl_axes_1,
            label ="Slice Z-Height",
            valmin=0,
            valmax=PLOTSIZE,
            valstep=1,
            valinit=0,
            orientation="vertical"
        )
        xy_slice_slider.on_changed(self._updateXYSlice)

        sl_axes_2 = fig.add_axes([0.4, 0.2, 0.025, 0.6])
        yz_slice_slider = Slider(
            ax = sl_axes_2,
            label ="Slice X-Height",
            valmin=0,
            valmax=PLOTSIZE,
            valstep=1,
            valinit=0,
            orientation="vertical"
        )
        yz_slice_slider.on_changed(self._updateYZSlice)

        sl_axes_3 = fig.add_axes([0.7, 0.2, 0.025, 0.6])
        xz_slice_slider = Slider(
            ax = sl_axes_3,
            label ="Slice Y-Height",
            valmin=0,
            valmax=PLOTSIZE,
            valstep=1,
            valinit=0,
            orientation="vertical"
        )
        xz_slice_slider.on_changed(self._updateXZSlice)

        plt.show()


if __name__ == "__main__":
    plotting = SoundSimPlot()

    if sim3D:
        plotting.plotSimulation3D()
    else:
        plotting.plotSimulation2D()
