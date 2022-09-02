"""
Pyqtgraph plot widgets with some presets

@author: Teddy Tortorici
"""

from PySide6.QtGui import QPen
import pyqtgraph as pg


class Plot(pg.PlotWidget):

    def __init__(self, x_label: str, y_label: str, legend: bool = True,
                 right_axis: pg.ViewBox = None, date_axis_item: bool = False):
        """
        Create a plot widget with some shortcuts
        :param x_label: Label for the x-axis
        :param y_label: Label for the y-axis
        :param right_axis: a view box you wish to plot to the right axis
        :param date_axis_item: for time.time() style time stamp data on the x-axis
        """
        super(self.__class__, self).__init__()
        self.x_label = x_label
        self.y_label = y_label
        self.right_axis = right_axis
        self.setLabel('bottom', x_label)
        self.setLabel('left', y_label)
        if date_axis_item:
            self.setAxisItems({'bottom': pg.DateAxisItem('bottom')})

        if legend:
            self.addLegend()

        if self.right_axis:
            self.showAxis('right')
            self.scene().addItem(right_axis)
            self.getAxis('right').linkToView(right_axis)
            self.setXLink(right_axis)
            self.setLabel('right', right_axis.label)
            self.update_views()
            self.getViewBox().sigResized.connect(self.update_views)

        self.curves = None
        self.x_indices = None
        self.y_indices = None

    def update_views(self):
        self.right_axis.setGeometry(self.getViewBox().sceneBoundingRect())
        self.right_axis.linkedViewChanged(self.getViewBox(), self.right_axis.XAxis)

    def set_curves(self, labels: list[str] | tuple[str], pens: list[QPen] | tuple[QPen]):
        self.curves = [self.plot(name=label, pen=pen) for label, pen in zip(labels, pens)]

    def set_indices(self, x_indices: list[int], y_indices: list[int] | zip):
        self.x_indices = x_indices
        self.y_indices = list(y_indices)

    def update(self, data):
        if isinstance(self.y_indices[0], list | tuple):
            
        else:
            for curve, x_index, y_index in zip(self.curves, self.x_indices, self.y_indices):
                curve.setData(x=data[:, x_index], y=data[:, y_index])


class RightAxisPlot(pg.ViewBox):
    def __init__(self, label: str):
        super(self.__class__, self).__init__()
        self.label = label

        self.curves = None
        self.x_indices = None
        self.y_indices = None

    def set_curves(self, labels: list[str] | tuple[str], pens: list[QPen] | tuple[QPen]):
        num = len(labels)
        self.curves = [None] * num
        for ii, label, pen in zip(range(num), labels, pens):
            self.curves[ii] = pg.PlotCurveItem(name=label, pen=pen)
            self.addItem(self.curves[ii])

    def set_indices(self, x_indices: list[int], y_indices: list[int] | zip):
        self.x_indices = x_indices
        self.y_indices = y_indices