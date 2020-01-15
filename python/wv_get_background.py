"""
Module for determining the background in a signal.
Approximate implementation of the method described in Galloway et al. (2009),
An iterative algorithm for background removal in spectroscopy by wavelet transforms, ),
which finds the background using an iterative wavelet filtering method .Applied Spectroscopy, 63, 1370

Depends on wv_denoise

It's a bit slow...
"""

import copy

import numpy as np

from wv_denoise import wv_denoise


# ----------------------------
__author__ = "L. Kogan"
# ----------------------------


# ----------------------------
def recursive_wv(data, ind_times, currentiter=0, niter=10, nlevels=12):
    """
    Recursively find background of the data

    :param data: data
    :param ind_times: time indices of background regions
    :param currentiter: current iteration number
    :param niter: total number of iterations
    :param nlevels: number of levels for the wavelet filtering
    """

    filt_data = wv_denoise(data, family="db15", ncoeff=1, nlevels=nlevels)
    filt_data = np.float64(filt_data)

    diff = data - filt_data

    ind_peaks = np.where(diff > 0)[0]
    ind_peaks = np.intersect1d(ind_times, ind_peaks)

    data[ind_peaks] = filt_data[ind_peaks]

    currentiter += 1

    if currentiter >= niter:
        return filt_data
    else:
        return recursive_wv(
            data, ind_times, currentiter=currentiter, niter=niter, nlevels=nlevels
        )


# ----------------------------
def wv_get_background(time, data, start_time, end_time, nlevels=12):
    """
    Use wavelet filtering to determine the background for a data set

    :param time: array of time values
    :param data: array of data values
    :param start_time: time before which signal can be considered to be background
    :param end_time: time after which signal can be considered to be background
    :param nlevels: number of levels to use for the wavelet filtering
    :return: background
    """

    ind_times = np.where((time > start_time) & (time < end_time))[0]

    data_copy = np.float64(copy.deepcopy(data))
    filt_data = recursive_wv(data_copy, ind_times, niter=5, nlevels=nlevels)

    return filt_data
