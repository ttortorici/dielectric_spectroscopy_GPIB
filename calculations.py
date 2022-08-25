import numpy as np
from scipy import special
from scipy import optimize
import os
import csv

eps0 = 8.85e-6  # electric constant in nF/um
epsS = 3.9      # relative dielectric constant of silica
hS = 500        # [um] silica substrate thickness
N = 52          # number of fingers on capacitor
L = 1000        # [um] capacitor finger length
u = 20          # [um] gap-finger unit cell size


def bare_capacitance(g):
    ka = k_air(g)
    ks = k_mat(g, hS)
    return 2 * (N - 1) * L * eps0 * (elliptic_over_comp(ka) + (epsS - 1) * elliptic_over_comp(ks) / 2)


def elliptic_over_comp(k):
    return special.ellipk(k) / special.ellipk(np.sqrt(1 - k**2))


def find_gap(bareC):
    def func(g):
        return bare_capacitance(g) - bareC
    return optimize.fsolve(func, 10)[0]


def geometric_capacitance(g, h):
    """Calculates the geometric capacitance for an interdigital capacitor given
    h - the thickness of the film
    g - gap size of the capacitor"""
    k = k_mat(h, g)
    return eps0 * (N - 1) * L * np.pi * (1 + k / 4) / (5 * np.log(2) - 2 * np.log(k))


def k_air(g):
    """Calculates k for K(k) calculation for h -> inf
    g - gap size"""
    return (u - g) / (u + g) * np.sqrt(2 * (u - g) / (2 * u - g))


def k_mat(g, h):
    """Calculates k for K(k) calculation
    h - thickness of film
    g - gap size"""
    return sinhpi4(u - g, h) / sinhpi4(u + g, h) * np.sqrt((sinhpi4(3 * u - g, h) ** 2 - sinhpi4(u + g, h) ** 2)
                                                           / (sinhpi4(3 * u - g, h) ** 2 - sinhpi4(u - g, h) ** 2))


def sinhpi4(x, h):
    return np.sinh(np.pi * x / (4 * h))


def load_calibration(name: str, capacitance_order: int = 2, loss_order: int = 1) -> tuple[np.ndarray]:
    """
    Calculates fit parameters from loading a calibration file
    :param name: path+filename
    :param capacitance_order: polynomial order of fit for capacitance
    :param loss_order: polynomial order of fit for loss tangent
    :return: tuple of fit parameters for capacitance and loss. Each is a numpy array
    """
    cal_data = np.loadtxt(os.path.join(name), comments='#', delimiter=',', skiprows=3)
    with open(name) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if len(row) > 1:        # this will grab the first line with the labels
                labels = row
                break
    temperature_indices = []        # indexes for temperatures
    capacitance_indices = []        # indexes for capacitance
    loss_indices = []               # indexes for loss tangent

    for ii, label in enumerate(labels):
        if 'temperature' in label.lower() and 'B' not in label:
            temperature_indices.append(ii)
        elif 'capacitance' in label.lower():
            capacitance_indices.append(ii)
        elif 'loss tangent' in label.lower():
            loss_indices.append(ii)

    capacitance_fit_parameters = [0] * len(temperature_indices)
    loss_fit_parameters = [0] * len(temperature_indices)
    for ii in range(capacitance_fit_parameters):
        capacitance_fit_parameters[ii] = np.polyfit(cal_data[:, temperature_indices[ii]],
                                                    cal_data[:, capacitance_indices[ii]],
                                                    2)
        loss_fit_parameters[ii] = np.polyfit(cal_data[:, temperature_indices[ii]],
                                             cal_data[:, loss_indices[ii]],
                                             1)

    return capacitance_fit_parameters[::-1], loss_fit_parameters[::-1]
