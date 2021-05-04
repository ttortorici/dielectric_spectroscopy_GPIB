"""Script for plotting for presentation"""

import matplotlib.pylab as plt

class Plot:
    def __init__(self, fig, title, axes_labels=['', ''], legend_loc=None, ):
        self.figure = fig
        self.title = title
        self.axes_labels = axes_labels
        plt.figure(fig)
        plt.title(title)
        plt.x_label(axes_labels[0])
        plt.y_label(axes_labels[1])
