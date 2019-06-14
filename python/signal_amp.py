"""
Class for reading and storing KG1 amplitude signals.

Inherits from SignalBase (signal_base.py).

Additional functionality for finding bad points,
and checking if the amplitude is valid in general
"""

import logging

import numpy as np

from signal_base import SignalBase

logger = logging.getLogger(__name__)

# ----------------------------
__author__ = "L. Kogan"
# ----------------------------


class SignalAmp(SignalBase):

    # The thresholds which the amplitude at start of the time trace
    # must exceed
    KG1C_START_AMP_BAD = 0.2
    KG1R_START_AMP_BAD = 3500
    KG1V_START_AMP_BAD = 0.5

    # The time before which the amplitude is checked
    KG1R_TIME_AMP_CHECK = 38.5
    KG1V_TIME_AMP_CHECK = 32.0

    # ------------------------
    def __init__(self, constants):
        """
        Initialisation for the class

        :param constants: Instance of Kg1Consts, containing useful constants & node names for JPFs, PPFs

        """
        self.signal_type = ""  # KG1R, KG1C, KG1V
        self.dcn_or_met = ""  # dcn or met

        # To be an array with the same number of time points as the signal, 
        # but with 0 or 1 to indicate points with a bad amplitude
        self.bad_points = None
        super(SignalAmp, self).__init__(constants)

    # ------------------------
    def read_data_ppf(self, dda, dtype, shot_no, signal_type, dcn_or_met):
        """
        Overide read_data_ppf method, to include additional
        argument to set the signal type & dcn_or_met.

        :param dda: DDA
        :param dtype: DTYPE
        :param shot_no: shot number
        :param signal_type: String to indicate if this is KG1R, KG1C or KG1V
        :param dcn_or_met: "dcn" or "met" depending on whether signal is from DCN or MET laser

        """
        self.signal_type = signal_type

        self.dcn_or_met = dcn_or_met

        super(SignalAmp, self).read_data_ppf(dda, dtype, shot_no)

    # ------------------------
    def read_data_jpf(self, signal_name, shot_no, signal_type, dcn_or_met):
        """
        Overide read_data_jpf method, to include additional argument to set the signal type
        and check the amplitude of the signal

        :param signal_name: JPF signal name
        :param shot_no: shot number
        :param signal_type: Identifies whether data is KG1C or KG1R or KG1V
        :param dcn_or_met: "dcn" or "met", ie. signal is from DCN or MET laser
        :returns: 0: Amplitude was read in and is OK,
                  9: Error reading the JPF signal,
                  10: The amplitude is bad

        """

        self.signal_type = signal_type

        self.dcn_or_met = dcn_or_met

        super(SignalAmp, self).read_data_jpf(signal_name, shot_no)

        if self.data is None or self.time is None:
            return 9

        if self.signal_type.startswith("kg1c"):
            amp_ok = self._check_amp_kg1c()
        elif self.signal_type.startswith("kg1r"):
            amp_ok = self._check_amp_average(self.KG1R_TIME_AMP_CHECK, self.KG1R_START_AMP_BAD)
        elif self.signal_type.startswith("kg1v"):
            amp_ok = self._check_amp_average(self.KG1V_TIME_AMP_CHECK, self.KG1V_START_AMP_BAD)
        else:
            amp_ok = False

        if not amp_ok:
            return 10

        return 0

    # ------------------------
    def find_bad_points(self):
        """
        Find points with a bad amplitude.

        - For KG1C, CPRB should be within a valid range
        - For KG1R & KG1V the amplitude should be above a certain value

        :return indices of bad points

        """
        if self.signal_type.startswith("kg1c"):
            cprb_mid = self.constants.cprb_mid_dcn
            cprb_range = self.constants.cprb_range_dcn

            if self.dcn_or_met == "met":
                cprb_mid = self.constants.cprb_mid_met
                cprb_range = self.constants.cprb_range_met

            ind_bad_amp, = np.where(np.absolute(self.data - cprb_mid) > cprb_range)
        elif self.signal_type.startswith("kg1r"):
            ind_bad_amp, = np.where(np.absolute(self.data) < self.constants.min_amp_kg1r)
        elif self.signal_type.startswith("kg1v"):
            ind_bad_amp, = np.where(np.absolute(self.data) < self.constants.min_amp_kg1v)
        else:
            ind_bad_amp = np.arange(0)

        return ind_bad_amp

    # ------------------------
    def _check_amp_average(self, time, threshold):
        """
        Check the average amplitude at the start of the pulse is high enough.
        For use with KG1R or KG1V

        :return: good_amp : True if the amplitude is good, false otherwise
        """
        logger.log(5, "Checking average amplitude exceeds threshold.")

        ind_start = np.where(self.time < time)

        good_amp = (np.absolute(np.mean(self.data[ind_start])) > threshold)

        if not good_amp:
            logger.debug ("Average amplitude is bad at the start: {}".format(np.mean(self.data[ind_start])))

        return good_amp

    # ------------------------
    def _check_amp_kg1c(self):
        """
        Check the CPRB signal (the KG1C frequency, which acts as the amplitude here).
        The CPRB signal at the start of the pulse should be within 80% of cprb_mid.
        It should also not fall below this value by more than cprb_range too many times
        in the whole pulse.
        cprb_mid and cprb_range are different for DCN and MET lasers.

        :return: good_amp : True if the amplitude is good, false otherwise
        """
        logger.log(5, "Checking KG1C CPRB signal is in expected range.")

        cprb_mid = self.constants.cprb_mid_dcn
        cprb_range = self.constants.cprb_range_dcn

        if self.dcn_or_met == "met":
            cprb_mid = self.constants.cprb_mid_met
            cprb_range = self.constants.cprb_range_met

        # Correct amp signal for early test jumps
        ind_31 = np.where(self.time < 31.004)[0]
        self.data[ind_31] = cprb_mid

        amp_cf_mid = self.data - cprb_mid

        ind_test_drops = (np.where((self.time > 31.05) & (self.time < 32.0) & (amp_cf_mid < -1.0*cprb_range)))[0]
        if len(ind_test_drops) > 0:
            self.data[ind_test_drops] = cprb_mid

        # Check for whether the amplitude is very low at the beginning of the trace
        ind_start = np.where((self.time > 31.15) & (self.time < 32.0))
        good_amp = ((np.absolute(np.mean(self.data[ind_start]) - cprb_mid) / cprb_mid) < self.KG1C_START_AMP_BAD)

        if not good_amp:
            logger.debug("Bad amplitude: KG1C CPRB is bad at the start: {}".format(np.mean(self.data[ind_start])))
            return good_amp

        # Check over the rest of the time range for loads of CPRB drops
        ind_rest = np.where(self.time > 31.15)
        ind_drops = np.where(amp_cf_mid[ind_rest] < -1.0*cprb_range)[0]

        good_amp = (len(ind_drops) < 5000)

        if not good_amp:
            logger.debug("Bad amplitude: KG1C CPRB drops below valid range {} times".format(len(ind_drops)))

        return good_amp

