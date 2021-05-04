import matplotlib.pylab as plt
import numpy as np
import os
import scipy.optimize as optimize
from scipy import stats

class Barrier_analysis:
    def __init__(self, temperatures_total, losses_total, freqs_total, cutoff=0.002):
        accept = np.where(losses_total > cutoff)
        self.temperatures = temperatures_total[accept]
        self.losses = losses_total[accept]
        self.freqs = freqs_total[accept]
        self.frequencies_unique = np.sort(np.unique(self.freqs))
        if self.frequencies_unique[0] == -1:
            self.frequencies_unique = np.delete(self.frequencies_unique, 0)
        freq_locs = {}
        for freq in self.frequencies_unique:
            freq_locs[str(freq)] = np.where(self.freqs == freq)
        self.temp_peak = np.zeros(len(self.frequencies_unique))
        self.a = np.zeros(len(self.frequencies_unique))
        self.b = np.zeros(len(self.frequencies_unique))
        self.sigmaTp = np.zeros(len(self.frequencies_unique))
        self.coeff = [0] * len(self.frequencies_unique)
        for ii, freq in enumerate(self.frequencies_unique):
            loss = self.losses[freq_locs[str(freq)]]
            temp = self.temperatures[freq_locs[str(freq)]]
            #Tp, a, b = optimize.curve_fit(sech_sqr, temp, loss)
            self.coeff[ii], cov = np.polyfit(temp, loss, 2, cov=True)
            self.temp_peak[ii] = -self.coeff[ii][1]/(2*self.coeff[ii][0])
            self.sigmaTp[ii] = np.sqrt(cov[1, 1]/(2*self.coeff[ii][0])**2
                                       + cov[0, 0]*(self.coeff[ii][1]/(2*self.coeff[ii][0]))**2)
        slope, intercept, r_val, p_val, stderr = stats.linregress(np.log(self.frequencies_unique), 1./self.temp_peak)
        self.E_B = -1./slope
        self.tau0 = np.exp(intercept/slope)/(2*np.pi)

        """    popt, pcov = optimize.curve_fit(inv_parabola, temp, loss)
            self.temp_peak[ii] = popt[0]
            self.a[ii] = popt[1]
            self.b[ii] = popt[2]
        popt, self.pcov = optimize.curve_fit(ln_f, 1. / self.temp_peak, np.log(self.frequencies_unique))
        #E_B optimize.curve_fit(ln_f, 1./temp_peak, np.log(frequencies_unique))
        self.E_B = popt[0]
        self.tau0 = popt[1]"""

    def plot(self):
        self.p = Plot('ln omega vs 1 over T', [r'ln($\omega$)', r'1/T (mK$^{-1}$)'])
        self.p.plot_std(np.log(self.frequencies_unique), 1./self.temp_peak*1000, self.sigmaTp/self.temp_peak**2)
        freq_lin = np.linspace(self.frequencies_unique[0]*0.8, self.frequencies_unique[-1]*1.3, 10)
        self.p.plot(np.log(freq_lin), (-np.log(2*np.pi*self.tau0*freq_lin)/self.E_B)*1000, plot_range=None, shape='-')
        self.p.ax.set_xlim()

    """def plot(self):
        self.p = Plot('ln omega vs T', ['T', r'ln($\omega$)'])
        self.p.plot(self.temp_peak, np.log(self.frequencies_unique))
        temp_lin = np.linspace(40, 100, 10)
        self.p.plot(temp_lin, ln_f_func(1. / temp_lin, self.E_B, self.tau0), plot_range=None, shape='-')
        self.p.ax.set_xlim()"""


class Plot:

    font = {'size': 28, 'color': 'k'}

    def __init__(self, title, axes_labels, legend_loc=None):
        self.title = title
        self.axes_labels = axes_labels
        self.legend_loc = legend_loc

        plot_size = np.array([6, 5]) * 1.2

        self.fig, self.ax = plt.subplots()
        self.fig.set_size_inches(plot_size[0], plot_size[1], forward=True)

        #self.fig.suptitle(self.title, fontsize=Plot.font['size'])

        """set axes labels"""
        self.ax.set_xlabel(axes_labels[0], fontsize=Plot.font['size'], color=Plot.font['color'], labelpad=10)
        self.ax.set_ylabel(axes_labels[1], fontsize=Plot.font['size'], color=Plot.font['color'], labelpad=10)

        self.ax.tick_params(axis='both', which='major', pad=15)
        self.ax.xaxis.set_tick_params(length=6, width=1)
        self.ax.yaxis.set_tick_params(length=6, width=1)
        """edit tick labels"""
        for tl in self.ax.get_yticklabels():
            tl.set_color(Plot.font['color'])
            tl.set_fontsize(Plot.font['size'])

        for tl in self.ax.get_xticklabels():
            tl.set_color(Plot.font['color'])
            tl.set_fontsize(Plot.font['size'])

        #plt.yticks(rotation=90)
        #self.axR = self.axL.twinx()

        for axis in ['top', 'bottom', 'left', 'right']:
            self.ax.spines[axis].set_linewidth(1.2)
        self.ax.axhline(color="k")
        self.ax.axvline(color="k")

        self.ax.get_xaxis().get_major_formatter().set_useOffset(False)
        self.ax.get_yaxis().get_major_formatter().set_useOffset(False)

        """Set the edges of the plot"""
        plt.tight_layout()
        if 'loss' in title.lower():
            self.fig.subplots_adjust(top=0.95, bottom=0.225, left=0.275, right=0.94)
        else:
            self.fig.subplots_adjust(top=0.95, bottom=0.225, left=0.25, right=0.94)
        #self.fig.subplots_adjust(top=0.95, bottom=0.225, left=0.15, right=0.94)
        #self.fig.subplots_adjust(bottom=.2)
        #self.fig.subplots_adjust(left=.25)
        #self.fig.subplots_adjust(right=)

        ticklines = self.ax.get_xticklines() + self.ax.get_yticklines()
        #gridlines = self.axL.get_xgridlines() + self.axL.get_ygridlines()

        for line in ticklines:
            line.set_linewidth(3)

        #for line in gridlines:
        #    line.set_linestyle('-')

    def plot(self, x, y, plot_range=None, shape='o', color='k', label=''):
        """Plots y vs x; marker: search 'pyplot.plot' at http://matplotlib.org/api/pyplot_api.html"""
        self.ax.plot(x, y, shape, label=label, markersize=5, markeredgewidth=1,
                     markerfacecolor='None', markeredgecolor=color)
        if plot_range:
            self.ax.set_ylim(plot_range[0:2])
            plt.yticks(np.arange(plot_range[0], plot_range[1], plot_range[2]))

    def plot_std(self, x, y, std):
        self.ax.errorbar(x, y, yerr=std, fmt='o')

    def plot_sep_freq(self, x, y, freqs, x_range=None, y_range=None, label=''):
        """plot something separating frequencies"""
        frequencies_unique = np.sort(np.unique(freqs))
        if frequencies_unique[0] == -1:
            frequencies_unique = np.delete(frequencies_unique, 0)
        pen = ['k', 'r', 'b']
        freq_locs = {}
        for freq in frequencies_unique:
            freq_locs[str(freq)] = np.where(freqs == freq)
        for ii, freq in enumerate(frequencies_unique):
            self.plot(x[freq_locs[str(freq)]], y[freq_locs[str(freq)]], plot_range=y_range,
                      shape='o', color=pen[ii], label='%s %d Hz' % (label, freq))
        if x_range:
            self.ax.set_xlim(x_range[0:2])
            plt.xticks(np.arange(x_range[0], x_range[1]+x_range[2], x_range[2]))
        self.legend()

    def plot_peaks(self, temperature, loss, freqs):
        frequencies_unique = np.sort(np.unique(freqs))
        if frequencies_unique[0] == -1:
            frequencies_unique = np.delete(frequencies_unique, 0)
        b = Barrier_analysis(temperature, loss, freqs)
        self.plot_sep_freq(temperature, loss, freqs)
        temp_lin = np.linspace(temperature[0], 120, 200)
        for ii, freq in enumerate(frequencies_unique):
            p = np.poly1d(b.coeff[ii])
            self.plot(temp_lin, p(temp_lin), plot_range=None, shape='-')
        self.ax.set_xlim(0, 120)
        self.ax.set_ylim(0, np.max(loss)+0.0002)

    def legend(self):
        if not self.legend_loc == None:
            plt.legend(loc=self.legend_loc)

    def save(self, filepath):
        path_to_save = os.path.join(filepath, 'plots')

        if not os.path.exists(path_to_save):
            os.makedirs(path_to_save)

        plt.savefig(os.path.join(path_to_save, self.title),
                    dpi=None, facecolor='w', edgecolor='w',
                    orientation='portrait', papertype=None, format=None,
                    transparent=False, bbox_inches=None, pad_inches=0.1,
                    frameon=None)


def inv_parabola(T, Tp, a, b):
    return -a*(T-Tp)**2+b


def sech_sqr(T, Tp, a, b):
    return a/np.cosh(T-Tp)**2+b


def ln_f_func(inv_Tp, E_B, tau0):
    return -np.log(2*np.pi*tau0) - E_B*inv_Tp

def one_over_T(ln_f, ln_twopi_tau_over_EB, one_over_E_B):
    return -ln_twopi_tau_over_EB - one_over_E_B * ln_f

def show():
    plt.show()
