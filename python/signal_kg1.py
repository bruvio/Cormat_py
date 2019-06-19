"""
Class for reading and storing KG1 signals.

Inherits from SignalBase (signal_base.py).

Additional functionality for correcting fringe 
jumps and storing status flags
"""

import logging
import copy

import numpy as np
from signal_base import SignalBase
from make_plots import make_plot
from kg4_data import Kg4Data
from library import *

logger = logging.getLogger(__name__)

# ----------------------------
__author__ = "B. Viola"
# ----------------------------


class SignalKg1(SignalBase):


    # ------------------------
    def __init__(self, constants,shot_no):
        """
        Init function

        :param constants: Instance of Kg1Consts, containing useful constants & all node names for PPF & JPFs

        """
        self.signal_type = ""  # kg1r, kg1c, kg1v
        self.dcn_or_met = "" # dcn, met
        self.corrections = SignalBase(constants)  # Corrections that have been made
        self.correction_type = np.arange(0) # For debugging : to keep track of where corrections have been made
        self.correction_dcn = np.arange(0) # For use with the lateral channels
        self.correction_met = np.arange(0) # For use with the lateral channels

        self.pulse = shot_no

        super(SignalKg1, self).__init__(constants)

        self.dfr = self.constants.DFR_DCN

    # ------------------------
    def __deepcopy__(self, memo):
        """
        Override deepcopy. Only a few of the attributes need to be copied.

        :param memo:

        """
        dpcpy = self.__class__(self.constants,0)

        if self.corrections.data is not None:
            dpcpy.corrections.data = self.corrections.data.copy()
        if self.corrections.time is not None:
            dpcpy.corrections.time = self.corrections.time.copy()
        if self.correction_type is not None:
            dpcpy.correction_type = self.correction_type.copy()
        if self.correction_dcn is not None:
            dpcpy.correction_dcn = self.correction_dcn.copy()
        if self.correction_met is not None:
            dpcpy.correction_met = self.correction_met.copy()
        if self.data is not None:
            dpcpy.data = self.data.copy()
        if self.time is not None:
            dpcpy.time = self.time.copy()
        dpcpy.dfr = self.dfr
        dpcpy.signal_type = self.signal_type
        dpcpy.dcn_or_met = self.dcn_or_met

        return dpcpy


    # ------------------------
    def uncorrect_fj(self, corr, index,fringe_vib=None):
        """
        Uncorrect a fringe jump by corr, from the time corresponding to index onwards.
        Not used ATM. Will need more testing if we want to use it... Suspect isclose is wrong.
        07mar2019
        used this function instead of is close as there is an issue with types and the value we are looking for
        sometimes are not found

        :param corr: Correction to add to the data
        :param index: Index from which to make the correction

        """
        # # Check we made a correction at this time.


        ind_corr, value = find_nearest(self.corrections.time, self.time[index])
        # ind_corr = np.where(np.isclose(self.corrections.time, self.time[index], atol=1e-3, rtol=1e-6) == 1)
        if np.size(ind_corr) == 0:
            logger.error('no correction to Undo!')
            return
        logger.log(5,
                   "From index {}, time {}, subtracting {} ({} fringes)".format(
                       ind_corr, value,
                       corr, corr / self.constants.DFR_DCN))
        # Uncorrect correction
        if fringe_vib is None:
            self.data[index:] = self.data[index:] + corr


        else:
            self.data[index:] = self.data[index:] + fringe_vib


        self.corrections.data = np.delete(self.corrections.data, ind_corr)
        self.corrections.time = np.delete(self.corrections.time, ind_corr)


    # ------------------------
    def correct_fj(self, corr, time=None, index=None, store=True, corr_dcn=None, corr_met=None,lid=None):
        """
        Shifts all data from time onwards, or index onwards,
        down by corr. Either time or index must be specified

        :param corr: The correction to be subtracted
        :param time: The time from which to make the correction (if this is specified index is ignored)
        :param index: The index from which to make the correction
        :param store: To record the correction set to True
        :param corr_dcn: Only for use with lateral channels. Stores the correction,
                         in terms of the number of FJ in DCN laser (as opposed to in the combined density)
        :param corr_met: Only for use with lateral channels. Stores the correction,
                         in terms of the number of FJ in the MET laser (as opposed to the correction in the vibration)

        """

        if time is None and index is None:
            logger.warning("No time or index was specified for making the FJ correction.")
            return

        if time is not None:
            index = np.where(self.time > time),
            if np.size(index) == 0:
                logger.warning("Could not find time near {} for making the FJ correction.".format(time))
                return

            index = np.min(index)


        self.data[index:] = self.data[index:] - corr

        # Store correction in terms of number of fringes
        if lid is None:
            corr_store = int(corr / self.constants.DFR_DCN)
        else:
            corr_store = lid

        logger.log(5,
                   "From index {}, time {}, subtracting {} ".format(
                       index, self.time[index],
                       corr))

        # If this is a mirror movement signal, store raw correction
        if ("vib" in self.signal_type):
                corr_store = corr





        if store:
            # Store in terms of the number of fringes for density, or vibration itself for vibration
            if self.corrections.data is None:
                self.corrections.data = np.array([corr_store])
                self.corrections.time = np.array([self.time[index]])
            else:
                self.corrections.data = np.append(self.corrections.data, corr_store)
                self.corrections.time = np.append(self.corrections.time, self.time[index])



            # Also store corresponding correction for the DCN & MET lasers (for use with lateral channels only)
            if corr_dcn is not None:
                self.correction_dcn = np.append(self.correction_dcn, corr_dcn)

            if corr_met is not None:
                self.correction_met = np.append(self.correction_met, corr_met)
