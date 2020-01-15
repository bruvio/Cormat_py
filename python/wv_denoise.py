"""
Module containg wv_densoise, a function to filter a signal using wavelet filtering.
Determination of threshold from ncoeff and percent is
done as in the idl function wv_denoise.pro.
"""

import pywt
import numpy as np
import math


# ----------------------------
__author__ = "L. Kogan"
# ----------------------------


def wv_denoise(signal, family=None, nlevels=None, ncoeff=None, percent=None):
    """
    Function to filter a signal using wavelet filtering.
    Determination of threshold from ncoeff and percent is
    done as in the idl function wv_denoise.pro.
    For more details on wavelet options see PyWavelet docs.
    If neither coeff or percent are specified then no filtering is
    done.

    TO DO:

           - Implement soft threshold
           - Thresholding using variance or something?
           - Think and check: divisible by 2 thing
           - 2D filter?

    :param signal: signal to be filtered.
    :param family: Wavelet family and order to use (default is 'db1')
    :param nlevels: Number of levels of DWT to perform. If none is given then
                    decomposition upto dwt_max_level is done, which
                    is the maximum useful level as computed by pyWavelets.
    :param ncoeff: The number of coefficients to retain when filtering.
                  If specified then percent is ignored.
    :param percent: The percentage of coefficients to retain when filtering.
                    If specified then coeff is ignored.
    :return: the filtered signal

    """

    if ncoeff is None and percent is None:
        return signal

    # Dimension should be divisible by 2
    signal = np.array(signal, dtype=np.dtype("d"))
    signal_length = len(signal)
    if signal_length % 2 > 0:
        signal = np.append(signal, signal[-1])

    # Remove mean so it doesn't swamp DWT
    mean = np.mean(signal)
    signal -= mean

    if family is None:
        family = "db1"

    if nlevels is not None:
        if nlevels > pywt.dwt_max_level(np.size(signal), pywt.Wavelet(family).dec_len):
            nlevels = None

    # Do transform to get coefficients
    coeffs = pywt.wavedec(signal, family, level=nlevels)

    # Do filtering
    detail_coeff = []
    for arr in coeffs[1:]:
        for el in arr:
            detail_coeff.append(el)

    if len(detail_coeff) == 0:
        return signal

    wps = np.absolute(detail_coeff) * np.absolute(detail_coeff)
    power = np.sum(wps)
    norm_wps = 100.0 * np.sort(wps)[::-1] / power

    cutoff = 0.0

    # If using percent
    if (percent is not None) and (ncoeff is None):
        cumul_power = np.cumsum(norm_wps)
        cumul_power[-1] = 100.0

        ncoeff = np.argmax(cumul_power >= percent)

    # Calculate threshold
    if ncoeff is not None:
        if ncoeff > len(detail_coeff):
            ncoeff = len(detail_coeff)

        cutoff = math.sqrt(norm_wps[ncoeff - 1] * power / 100.0)

    # Apply threshold
    for ind in range(len(coeffs[1:])):
        coeffs[ind + 1] = pywt.threshold(coeffs[ind + 1], cutoff, "hard")

    # Do inverse-transform
    filtered_signal = pywt.waverec(coeffs, family)

    # If we added an extra element to make the array divisible
    # by 2, adjust it back again.
    if len(filtered_signal) > signal_length:
        filtered_signal = filtered_signal[:-1]

    # Add mean back in
    filtered_signal += mean

    return filtered_signal
