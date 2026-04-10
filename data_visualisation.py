#!/usr/bin/env python3

from matplotlib.widgets import Slider
import matplotlib.pyplot as plt
import napari
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

        plt.xlabel(f"Distance (1 Cell is {CELL_SIDE_LENGTH_MM}mm)")
        plt.ylabel(f"Distance (1 Cell is {CELL_SIDE_LENGTH_MM}mm)")

        plt.gcf().canvas.manager.set_window_title("Sound Simulation")

        plt.show()

    def plotSimulation3D(self):
        """
        Calls the computation of the 3D data matrix, and then calls the desired visualisation function
        """
        self.data_matrix = runVectorisedSimulation3D()

        # Creates a standardised colour map for the heatmaps
        cmap = plt.get_cmap("plasma").copy()
        cmap.set_under("lightgrey")

        if VIEWMODE_3D == 0:
            self._slicesThroughVolumeVisualisation(cmap)
        elif VIEWMODE_3D == 1:
            self._volumetricView(cmap)

    def _volumetricView(self, cmap):
        """
        Uses napari to generate a volumetric view of the 3D data matrix
        """
        # Initialising the viewer
        viewer = napari.Viewer(ndisplay=3)

        # Adding my data to the viewer
        img = viewer.add_image(
            self.data_matrix,
            name="Ultrasound Intensity",
            colormap="inferno"
        )

        # Displaying a colorbar, and a box around the data cube
        img.colorbar.visible = True
        img.bounding_box.visible = True

        # Setting the startup camera view
        viewer.camera.zoom = 0.5
        viewer.camera.angles = (0, 30, 30)
        viewer.camera.center = (250, 250, 250)

        napari.run()

    def _updateXYSlice(self, val):
        """
        Slider callback function
        Updates the XY slice of the heatmap data being visualizes
        """
        self.im1.set_data(self.data_matrix[:, :, val])
        plt.draw()

    def _updateYZSlice(self, val):
        """
        Slider callback function
        Updates the YZ slice of the heatmap data being visualizes
        """
        self.im2.set_data(self.data_matrix[:, val, :].T)
        plt.draw()

    def _updateXZSlice(self, val):
        """
        Slider callback function
        Updates the XZ slice of the heatmap data being visualizes
        """
        self.im3.set_data(self.data_matrix[val, :, :].T)
        plt.draw()

    def _slicesThroughVolumeVisualisation(self, cmap):
        """
        Matplotlib visualisation for the 3D data
        Plots three 2D slices of the data cube, with sliders to let you slice through cross-sections of the data
        """
        # Creates a figure to plot on
        fig = plt.figure(figsize=(16, 5))
        fig.canvas.manager.set_window_title("Sound Simulation")

        # Creates axes to put my plots, sliders, and colourbar on
        ax1 = fig.add_axes([0.065, 0.15, 0.25, 0.75])
        ax2 = fig.add_axes([0.385, 0.15, 0.25, 0.75])
        ax3 = fig.add_axes([0.70, 0.15, 0.25, 0.75])

        sl_ax1 = fig.add_axes([0.02, 0.15, 0.01, 0.75])
        sl_ax2 = fig.add_axes([0.34, 0.15, 0.01, 0.75])
        sl_ax3 = fig.add_axes([0.655, 0.15, 0.01, 0.75])

        cbar_ax = fig.add_axes([0.96, 0.15, 0.01, 0.75])

        self.im1 = ax1.imshow(self.data_matrix[:, :, 0],
            cmap=cmap,
            interpolation="bilinear",
            origin="lower",
            vmax=self.data_matrix.max()
        )

        # Adding slider to control which slice is shown in the heatmaps
        xy_slice_slider = Slider(
            ax = sl_ax1,
            label ="Slice Z",
            valmin=0,
            valmax=PLOTSIZE,
            valstep=1,
            valinit=0,
            orientation="vertical"
        )
        xy_slice_slider.on_changed(self._updateXYSlice)

        # Repeating for other perspectives (XZ/YZ slices)

        self.im2 = ax2.imshow(self.data_matrix[:, 0, :].T,
            cmap=cmap,
            interpolation="bilinear",
            origin="lower",
            vmax=self.data_matrix.max()
        )

        yz_slice_slider = Slider(
            ax = sl_ax2,
            label ="Slice X",
            valmin=0,
            valmax=PLOTSIZE,
            valstep=1,
            valinit=0,
            orientation="vertical"
        )
        yz_slice_slider.on_changed(self._updateYZSlice)

        self.im3 = ax3.imshow(self.data_matrix[0, :, :].T,
            cmap=cmap,
            interpolation="bilinear",
            origin="lower",
            vmax=self.data_matrix.max()
        )

        xz_slice_slider = Slider(
            ax = sl_ax3,
            label ="Slice Y",
            valmin=0,
            valmax=PLOTSIZE,
            valstep=1,
            valinit=0,
            orientation="vertical"
        )
        xz_slice_slider.on_changed(self._updateXZSlice)

        fig.colorbar(self.im3, cax=cbar_ax)

        # Setting plot titles
        ax1.set_title(f"XY Ultrasound Intensity {"(dBA)" if dBA else "(dB)"}")
        ax2.set_title(f"YZ Ultrasound Intensity {"(dBA)" if dBA else "(dB)"}")
        ax3.set_title(f"XZ Ultrasound Intensity {"(dBA)" if dBA else "(dB)"}")

        ax1.set_xlabel(f"Distance (1 Cell is {CELL_SIDE_LENGTH_MM}mm)")
        ax2.set_xlabel(f"Distance (1 Cell is {CELL_SIDE_LENGTH_MM}mm)")
        ax3.set_xlabel(f"Distance (1 Cell is {CELL_SIDE_LENGTH_MM}mm)")
        ax1.set_ylabel(f"Distance (1 Cell is {CELL_SIDE_LENGTH_MM}mm)")
        ax2.set_ylabel(f"Distance (1 Cell is {CELL_SIDE_LENGTH_MM}mm)")
        ax3.set_ylabel(f"Distance (1 Cell is {CELL_SIDE_LENGTH_MM}mm)")

        plt.show()


if __name__ == "__main__":
    plotting = SoundSimPlot()

    if SIM3D:
        plotting.plotSimulation3D()
    else:
        plotting.plotSimulation2D()
