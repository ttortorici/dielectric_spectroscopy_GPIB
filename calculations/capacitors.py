import numpy as np
from scipy import special
from scipy import optimize
from decimal import Decimal

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


def elliptic_over_comp_small_k(k: float) -> float:
    """
    Small k approximation to the elliptic integral divided by its complement
    :param k: inputs of elliptic integrals calculated from k_ functions
    :return: approximation of elliptic integral divided by its compliment
    """
    ellip_integral = np.pi / 2 * (1 + k / 4 + 9 * k / 64)
    ellip_integral_comp = 5 / 2 * np.log(2) - np.log(k)
    return ellip_integral / ellip_integral_comp


def find_gap(bare_c_val):
    def func(g):
        return bare_capacitance(g) - bare_c_val
    return optimize.fsolve(func, np.array([10.]))[0]


def geometric_capacitance(g, h):
    """Calculates the geometric capacitance for an interdigital capacitor using the small k
    h - the thickness of the film
    g - gap size of the capacitor"""
    k = k_mat(h, g)
    return eps0 * (N - 1) * L * np.pi * (1 + k / 4) / (5 * np.log(2) - 2 * np.log(k))


def k_air(g):
    """Calculates k for K(k) calculation for h -> inf
    g - gap size"""
    return (u - g) / (u + g) * np.sqrt(2 * (u - g) / (2 * u - g))


def k_mat(g: float, h: float) -> float:
    """
    Calculates k for K(k) calculation down to 0.1 um material thickness
    :param g: gap size [um]
    :param h: thickness of film [um]
    :return: argument for elliptic integral
    """

    return sinhpi4(u - g, h) / sinhpi4(u + g, h) * np.sqrt((sinhpi4(3 * u - g, h) ** 2 - sinhpi4(u + g, h) ** 2)
                                                           / (sinhpi4(3 * u - g, h) ** 2 - sinhpi4(u - g, h) ** 2))


def k_film(g: float, h: float) -> float:
    """
    Calculates k for K(k) calculation for thin films down to 60 nm
    :param g: gap size [um]
    :param h: thickness of film [nm]
    :return: argument for elliptic integral
    """
    h /= 1e3    # convert from nm to um
    part1 = sinhpi4(3 * u - g, h)
    part2 = sinhpi4(u + g, h)
    part3 = sinhpi4(3 * u - g, h)
    part4 = sinhpi4(u - g, h)
    outside_sqrt = part4 / part2
    inside_sqrt = float((Decimal(part1) ** 2 - Decimal(part2) ** 2) / (Decimal(part3) ** 2 - Decimal(part4) ** 2))
    return outside_sqrt * np.sqrt(inside_sqrt)


def sinhpi4(x, h):
    return np.sinh(np.pi * x / (4 * h))
