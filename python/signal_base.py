"""
Class for reading and storing a signal from the PPF or JPF system, 
with functionality for filtering, resampling, and calculating the 
differences between adjacent time points.
"""

import logging

import numpy as np
from scipy import signal
# from getdat import getdat, getsca
from getdat import *
from ppf import ppfgo, ppfget, ppfssr, ppfuid

from wv_denoise import wv_denoise

logger = logging.getLogger(__name__)

# ----------------------------
__author__ = "L. Kogan"
# ----------------------------

from scipy.signal import firwin, lfilter, filtfilt, cheby1, lti
import numpy as np
def decimate_ZP(x, q, n=None, ftype='iir', axis=-1, zero_phase=False):
    """
    Downsample the signal by using a filter.
    By default, an order 8 Chebyshev type I filter is used.  A 30 point FIR
    filter with hamming window is used if `ftype` is 'fir'.
    Parameters
    ----------
    x : ndarray
        The signal to be downsampled, as an N-dimensional array.
    q : int
        The downsampling factor.
    n : int, optional
        The order of the filter (1 less than the length for 'fir').
    ftype : str {'iir', 'fir'}, optional
        The type of the lowpass filter.
    axis : int, optional
        The axis along which to decimate.
    zero_phase : bool
        Prevent phase shift by filtering with ``filtfilt`` instead of ``lfilter``.
    Returns
    -------
    y : ndarray
        The down-sampled signal.
    See also
    --------
    resample
    
    Notes
    -----
    The ``zero_phase`` keyword was added in 0.17.0.
    The possibility to use instances of ``lti`` as ``ftype`` was added in 0.17.0.
    """
    
    if not isinstance(q, int):
        raise TypeError("q must be an integer")

    if ftype == 'fir':
        if n is None:
            n = 30
        b = firwin(n + 1, 1. / q, window='hamming')
        a = 1.
    
    elif ftype == 'iir':
        if n is None:
            n = 8
        b, a = cheby1(n, 0.05, 0.8 / q)
    else:
        b = ftype.num
        a = ftype.den

    if zero_phase:    
        y = filtfilt(b, a, x, axis=axis)
    else:
        y = lfilter(b, a, x, axis=axis)

    sl = [slice(None)] * y.ndim
    sl[axis] = slice(None, None, q)
    return y[sl]

def gcd(a, b):
    """Compute the greatest common divisor of a and b"""
    while b > 0:
        a, b = b, a % b
    return a


def lcm(a, b):
    """Compute the lowest common multiple of a and b"""
    return a * b / gcd(a, b)


class SignalBase():
    # ------------------------
    def __init__(self, constants):
        """
        Initialise variables to hold the data and filtered data.
        :param constants: Instance of Kg1Consts, containing useful constants & node names
        """
        self.constants = constants
        self.data = None
        self.time = None
        self.ihdata = None # For use with PPF data
        self.iwdata = None # For use with PPF data


    # ------------------------
    def read_data_ppf(self, dda, dtype, shot_no, read_bad=False, read_uid="JETPPF", seq=0):
        """
        Read in and store PPF data
        :param dda: DDA
        :param dtype: DTYPE
        :param shot_no: shot number
        :param read_bad: If set to true, data is read in for all sequence numbers (even status == 4)
        :param read_uid: UID to use to read PPF data
        :param seq: sequence number to read in
        """
        logger.debug( "Reading in PPF signal {}/{} with uid {}".format(dda, dtype, read_uid))

        if dda == "" or dtype == "":
            return 0

        ier = ppfgo(shot_no, seq=seq)

        ppfuid(read_uid, rw="R")

        if read_bad:
            ppfssr([0,1,2,3,4])

        if ier != 0:
            return 0

        ihdata, iwdata, data, x, time, ier = ppfget(shot_no, dda, dtype)

        if ier != 0:
            return 0

        self.data = np.array(data)
        self.time = np.array(time)
        self.ihdata = ihdata
        self.iwdata = iwdata

        # Return the status flag
        return iwdata[11]

    # ------------------------
    def read_data_jpf(self, signal_name, shot_no, use_64bit=False):
        """
        Read in and store JPF data
        :param signal_name: Node name for JPF
        :param shot_no: shot number
        :param use_64bit: If set to true the data is stored as 64 bit float
        """
        self.pulse = shot_no
        logger.debug( "Reading in JPF signal {}".format(signal_name))

        if signal_name == "":
            return

        data, time, nwds, title, units, ier = getdat(signal_name, shot_no, nwds=-1)

        if ier != 0:
            return

        if use_64bit:
            self.data = np.array(data, dtype=np.float64)
            self.time = np.array(time)
        else:
            self.data = np.array(data)
            self.time = np.array(time)

    # ------------------------
    def read_data_jpf_1D(self, signal_name, shot_no):
        """
        Read in JPF data with only one dimension
        :param signal_name: signal name
        :param shot_no: shot number
        """
        logger.debug( "Reading in JPF 1D signal {}".format(signal_name))
        data, nwds, title, units, ier = getsca(signal_name, shot_no, nwds=0)

        if ier != 0:
            return

        if data[0] > 0.0:
            self.data = data

    # ------------------------
    def filter_signal(self, family, ncoeff=None, percent=None, start_time=0, end_time=0):
        """
        Filter the signal using wavelet filtering
        :param family: wavelet family to use for filtering
        :param ncoeff: number of coefficients to retain in the filtering
        :param percent: percentage of coefficients to retain in the filtering
        :param start_time: Time from which to start the filtering
        :param end_time: Time to finish the filtering
        :return: numpy array containing the filtered data from start_time - end_time
        """

        ind_start, ind_end = self.get_time_inds(start_time, end_time)

        return wv_denoise(self.data[ind_start:ind_end+1], family, ncoeff=ncoeff, percent=percent)

    # ------------------------
    def get_time_inds(self, start_time, end_time):
        """
        Get the index of the times corresponding to start_time and end_time
        :param start_time: start time
        :param end_time: end time
        :return: index of start_time, index of end_time
        """
        ind_start = 0
        ind_end = np.size(self.data)-1

        if end_time > 0.0:
            ind_after = np.where(self.time > start_time)[0]
            if len(ind_after) > 0:
                ind_start = ind_after[0]

            ind_before = np.where(self.time < end_time)[0]
            if len(ind_before) > 0:
                ind_end = ind_before[-1]

        return ind_start, ind_end

    # ------------------------
    def resample_signal(self, resample_method, new_time):
        """
        Resample the signal, to a different timebase,
        by
        -interpolation,
        -zeropadding
        :param resample_method: method to use
        :return: numpy array of resampled data
        """
        if resample_method == "interp":
            return np.interp(new_time, self.time, self.data)
        if resample_method =='zeropadding':
            # zero padding procedure
            M = len(self.time)
            N = len(new_time)
            ratioMN = int(M / N)
            # Out[5]: 4
            # ratioMN+1
            # increase vector so to have integer ratio between signals
            # (ratioMN+1)*N
            # Out[7]: 150195
            # number of point to add  to increase vector size so to have integer ratio between signals
            points = (ratioMN + 1) * N - M
            # Out[8]: 20200
            # In[7]: np.mean(np.diff(time_kg1r))
            # Out[9]: 0.00019999998
            # newtime base
            dt = np.mean(np.diff(self.time))
            ttt = np.arange(points + 1)[1:] * dt
            # In[10]: len(ttt)
            # Out[12]: 20200
            ttt = np.arange(points + 1)[1:] * dt + self.time[-1]
            # newtime=np.concatenate(time_kg1r, ttt)

            newtime = np.concatenate((self.time, ttt))
            resTime = newtime[::ratioMN + 1]
            # newtime.size
            # Out[17]: 150195
            # newtime.size/5
            # Out[18]: 30039.0
            xxx = np.zeros(points)
            newsig = np.concatenate((self.data, xxx))
            # In[19]: newsig.size
            # Out[21]: 150195
            # In[20]: newsig.size/5
            # Out[22]: 30039.0
#            resSig = signal.decimate(newsig, ratioMN + 1)
            resSig = decimate_ZP(newsig, ratioMN + 1, zero_phase=True)
            return resSig,resTime



        else:
            logger.warning("Unknown resampling method, data has not been resampled!")
            return self.data

    # ------------------------
    def get_differences(self, npoints):
        """
        Get the difference between the data npoints apart.
        :param npoints: Number of points over which to calculate the difference
        :return: numpy array of difference
        """
        diff = self.data[npoints:] - self.data[0:-1*npoints]
        return diff

    # ------------------------
    def get_second_differences(self, npoints):
        """
        Get the second differential over npoints
        :param npoints: Number of points over which to calculate the difference
        :return: numpy array of second differential
        """
        diff = self.data[npoints:] - self.data[0:-1*npoints]
        diff_second = diff[1:] - diff[0:-1]
        return diff_second

    # ------------------------
    def delete_points(self, ind_points):
        """
        Delete points with indices ind_points
        :param ind_points: indices of points to delete
        """
        self.data = np.delete(self.data, ind_points)
        self.time = np.delete(self.time, ind_points)

