import numpy as np
from data_loader import DataSet, load_data


def fit_bare(data_set, cp_order=3, lp_order=2):
    """data_set is an object of DataSet class"""
    fitsC = np.zeros((cp_order, len(data_set.frequencies)))        # 2nd order polynomial
    fitsL = np.zeros((lp_order, len(data_set.frequencies)))        # 1st order polynomial
    for ii, frequency in enumerate(data_set.frequencies):
        fitC[:, ii] = np.polyfit(data_set.T(frequency), data_set.C(frequency), cp_order)[::-1]     # returns a0, a1, a2
        fitL[:, ii] = np.polyfit(data_set.T(frequency), data_set.loss(frequency), lp_order)[::-1]  # returns b0, b1
    return fitsC, fitsL


