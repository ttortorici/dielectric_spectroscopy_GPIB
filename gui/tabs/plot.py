"""
A tab widget for plotting data in app.py

@author: Teddy Tortorici
"""

from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QToolButton, QMainWindow
from PySide6.QtCore import Slot
import gui.icons as icon
from gui.plotting import Plot, RightAxisPlot
from files.csv import CSVFile
import sys
import numpy as np
import pyqtgraph as pg


class PlotTab(QWidget):

    labels = ['time', 'temperature a', 'temperature b', 'capacitance', 'loss', 'voltage', 'frequency']
    colors = {"temperature": ((85, 179, 255),       # light blue
                              (75, 245, 215)),      # teal
              "capacitance": ((255, 125, 150),      # light red
                              (180, 165, 255),      # lighter blue
                              (220, 220, 220),      # light grey
                              (180, 255, 180),      # light green
                              (253, 254, 150),      # yellow
                              (255, 163, 102)),     # orange
              "loss": ((255, 105, 183),             # magenta
                       (205, 145, 255),             # light purple
                       (255, 255, 255),             # white
                       (204, 255, 137),             # lime
                       (249, 218, 122),             # yellow-orange
                       (255, 131, 102))}            # red-orange
    pen_width = 2
    # colors = [(0, 0, 255), (255, 0, 0), (0, 0, 0)]
    # pens = dict(zip(data_columns[1:], [pg.mkPen(color, width=2) for color in colors]))
    plot_colors = {"background": (42, 42, 38),      # dark mode
                   "foreground": (255, 255, 255)}   # white

    def __init__(self, parent: QMainWindow, link_x: bool = True, link_y: bool = False):
        """
        Tab for plotting
        :param parent: Is the MainWindow() object
        :param link_x: Do you want it to lock x axes of the same type together?
        :param link_y: Do you want it to lock y axes of the same type together?
        """
        QWidget.__init__(self)
        for key in PlotTab.plot_colors.keys():
            pg.setConfigOption(key, PlotTab.plot_colors[key])

        self.data_line_skip = 0
        self.live_plotting = True

        self.parent = parent

        self.filename = None

        main_layout = QHBoxLayout(self)
        plot_layout = QGridLayout()
        button_layout = QVBoxLayout()

        self.plot_CvT = Plot('Temperature (K)', 'Capacitance (pF)')
        self.plot_LvT = Plot('Temperature (K)', 'Loss Tangent')
        self.plot_Tvt = Plot('Time', 'Temperature (K)', date_axis_item=True)
        self.plot_Lvt = RightAxisPlot('Loss Tangent')
        self.plot_Cvt = Plot('Time', 'Capacitance (pF)', right_axis=self.plot_Lvt, date_axis_item=True)

        # Will place in the gid to mimic the list of lists
        plots = [[self.plot_CvT, self.plot_Tvt],
                 [self.plot_LvT, self.plot_Cvt]]

        """Link X and Y axes (if specified)"""
        if link_x or link_y:
            plot_list = [plot for plot_row in plots for plot in plot_row]       # flattens list of lists into a list
            for ii, plot_ii in enumerate(plot_list):
                for jj, plot_jj in enumerate(plot_list):
                    if ii < jj:
                        if link_x:
                            if plot_ii.x_label.lower() == plot_jj.x_label.lower():
                                plot_ii.setXLink(plot_jj)
                        if link_y:
                            if plot_ii.y_label.lower() == plot_jj.y_label.lower():
                                plot_ii.setYLink(plot_jj)

        """Place Plots in the grid layout"""
        for ii, plot_row in enumerate(plots):
            for jj, plot in enumerate(plot_row):
                plot_layout.addWidget(plot, ii, jj)

        """Place buttons in vertical layout"""
        self.button_update = QToolButton()
        self.button_update.setIcon(icon.built_in(self, 'BrowserReload'))
        self.button_update.setToolTip('Update Plots')
        self.button_update.clicked.connect(self.update_plots)

        self.button_play_pause = QToolButton()
        self.button_play_pause.clicked.connect(self.swap_live)
        self.set_live_plotting(True)

        buttons = [self.button_play_pause, self.button_update]
        for button in buttons:
            button_layout.addWidget(button)
        button_layout.addStretch(0)

        """Place layouts in main layout"""
        main_layout.addLayout(plot_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    @Slot(str)
    def initialize_plots(self, filename):
        """Second initialize for after the MainWindow() is completely done initializing"""
        self.filename = filename
        self.freq_labels = [str(freq) for freq in self.parent.data_tab.dialog.freq_entry]
        freq_num = len(self.freq_labels)
        labels = CSVFile.get_labels(self.filename)

        """CREATE CURVES"""
        width = self.__class__.pen_width

        colors = self.__class__.colors["capacitance"][:freq_num]
        pens = [pg.mkPen(color, width=width) for color in colors]
        self.plot_CvT.set_curves(self.freq_labels, pens)
        self.plot_Cvt.set_curves([f"C: {f}" for f in self.freq_labels], pens)

        colors = self.__class__.colors["capacitance"][:freq_num]
        pens = [pg.mkPen(color, width=width) for color in colors]
        self.plot_LvT.set_curves(self.freq_labels, pens)
        self.plot_Lvt.set_curves([f"L: {f}" for f in self.freq_labels], pens)

        colors = self.__class__.colors["temperature"][:freq_num]
        self.plot_Tvt.set_curves(["A", "B"], [pg.mkPen(color, width=width) for color in colors])

        """FIND INDEXES IN DATA"""
        time_indices = [ii for ii, ll in enumerate(labels) if 'time' in ll.lower()]
        temp_a_indices = [ii for ii, ll in enumerate(labels) if 'temperature a' in ll.lower()]
        temp_b_indices = [ii for ii, ll in enumerate(labels) if 'temperature b' in ll.lower()]
        cap_indices = [ii for ii, ll in enumerate(labels) if 'capacitance' in ll.lower()]
        loss_indices = [ii for ii, ll in enumerate(labels) if 'loss' in ll.lower()]

        self.plot_CvT.set_indices(temp_a_indices, cap_indices)
        self.plot_LvT.set_indices(temp_a_indices, loss_indices)
        self.plot_Tvt.set_indices(time_indices, zip(temp_a_indices, temp_b_indices))
        self.plot_Cvt.set_indices(time_indices, cap_indices)
        self.plot_Lvt.set_indices(time_indices, loss_indices)

        self.plot_Cvt.update_views()


    def set_live_plotting(self, on):
        """Turn live plotting on or off"""
        self.live_plotting = on
        self.button_update.setEnabled(not on)
        if on:
            self.button_play_pause.setIcon(icon.built_in(self, 'DialogYesButton'))
            self.button_play_pause.setToolTip('Live Plotting')
        else:
            self.button_play_pause.setIcon(icon.built_in(self, 'DialogNoButton'))
            self.button_play_pause.setToolTip('Click to turn on Live Plotting')

    @Slot()
    def swap_live(self):
        """Switch the live plotting setting"""
        self.set_live_plotting(not self.live_plotting)

    @Slot()
    def update_plots(self):
        """Draw curves to update the plots to any changes in the data file"""
        if self.parent.data_tab.active_file:
            data = self.load_data()
            time_data = data[:, 0]
            voltage_data = data[:, 1]
            temperature_data = data[:, 2]
            counts_data = data[:, 3]

            self.plot_TvV.curve.setData(x=voltage_data, y=temperature_data)
            self.plot_CvT.curve.setData(x=temperature_data, y=counts_data)
            self.plot_Tvt.curve.setData(x=time_data, y=temperature_data)
            self.plot_Vvt.curve.setData(x=time_data, y=voltage_data)
            self.plot_Cvt.curve.setData(x=time_data, y=counts_data)

    def load_data(self) -> np.ndarray:
        """Loads data from filename. Will make attempts to load data and if it fails, it will add to the amount of lines
        needed to skip. After the first attempt to load data, it should succeed on the first attempt every time"""
        data, self.data_line_skip = CSVFile.load_data_np(self.filename, self.data_line_skip)
        return data


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    main_window = PlotTab(QWidget())
    main_window.show()

    sys.exit(app.exec())
