import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSlot
from tab_measure import MeasureTab
from tab_control import ControlTab
from tab_plotter import PlotterTab


class MainTabs(qtw.QWidget):
    def __init__(self, parent, base_path):
        super(qtw.QWidget, self).__init__(parent)
        self.base_path = base_path
        self.layout = qtw.QVBoxLayout(self)
        self.parent = parent
        # print(parent.path)

        """Initialize tab screen"""
        self.tabs = qtw.QTabWidget()
        self.tabMeas = MeasureTab(self, self.base_path)
        self.tabPlot = PlotterTab(self, self.base_path)
        self.tabCont = ControlTab(self)
        self.tabMeas.init_controller_updates()

        """Add tabs"""
        self.tabs.addTab(self.tabMeas, "Measure")
        self.tabs.addTab(self.tabPlot, "Plot")
        self.tabs.addTab(self.tabCont, "Control")

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(),
                  currentQTableWidgetItem.text())