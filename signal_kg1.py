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

logger = logging.getLogger(__name__)

# ----------------------------
__author__ = "L. Kogan"
# ----------------------------


class SignalKg1(SignalBase):

    # Times of fake jumps at the start of the time trace (due to tests in the hardware)
    KG1R_FAKE_JUMP_TIMES = [39.4988]
    # KG1R_FAKE_JUMP_TIMES = [39.4993]
    KG1C_FAKE_JUMP_TIMES_DCN = [31.001, 31.002, 31.101, 31.111, 31.141]
    KG1C_FAKE_JUMP_TIMES_MET = [31.001, 31.002, 31.121, 31.131, 31.141]

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
        # Time range to calculate offset
        self.offset_time_kg1c = [31.0, 35.0]
        if self.pulse >= 92846:  # change in firmware: now the offset is computed by the firmware
            self.offset_time_kg1r = [37.0, 39.4993]
        else:
            self.offset_time_kg1r = [38.0, 39.0]
        self.offset_time_kg1v = [0.0, 30.0]
        self.offset_time = self.offset_time_kg1c
        self.offset_time_ind = [0,1]

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
    def read_data_ppf(self, dda, dtype, shot_no, signal_type, dcn_or_met):
        """
        Override read_data_ppf method, to include additional
        argument to set the signal type, dcn_or_met variable & appropriate DFR

        :param dda : DDA
        :param dtype : dtype
        :param shot_no : shot number
        :param signal_type : Identifies signal as KG1C or KG1R or KG1V
        :param dcn_or_met: "dcn" or "met" depending on whether signal is from DCN or MET laser

        """
        self.signal_type = signal_type
        self.dcn_or_met = dcn_or_met

        if self.dcn_or_met == "met":
            self.dfr = self.constants.DFR_MET

        super(SignalKg1, self).read_data_ppf(dda, dtype, shot_no)

    # ------------------------
    def read_data_jpf(self, signal_name, shot_no, signal_type, dcn_or_met, chan,
                      reverse_polarity=False, use_64bit=False):
        """
        Overide read_data_jpf method, to include additional
        argument to apply offset so the phase is zero at the start
        & check for a bad phase signal.
        Also sets the signal type, dcn_or_met variable & appropriate DFR

        :param signal_name: signal name
        :param shot_no: shot number
        :param signal_type: Identifies signal as KG1C or KG1R or KG1V
        :param dcn_or_met: "dcn" or "met" depending on whether signal is from DCN or MET laser
        :param chan: channel number
        :param reverse_polarity: switch sign of signal data if True
        :param use_64bit: store data in 64-bit floating point numpy array
        :returns: 0 : Phase was read in and is OK
                  9 : Error reading the JPF signal
                  10 : The phase is bad
        """

        self.signal_type = signal_type
        self.dcn_or_met = dcn_or_met

        if self.dcn_or_met == "met":
            self.dfr = self.constants.DFR_MET

        # Read in JPF data
        super(SignalKg1, self).read_data_jpf(signal_name, shot_no, use_64bit=use_64bit)

        if self.data is None or self.time is None:
            logger.log(5, "Could not read in JPF data.")
            return 9

        # If necessary, reverse polarity of the signal.
        # This is here just in case, normally it shouldn't be needed but in the past
        # cabling was the wrong way round for a number of shots & we needed to invert the signal.
        if reverse_polarity:
            logger.debug("Reversing the polarity of the phase.")
            self._reverse_polarity()

        jumps = [] # Keep a track of what jumps were corrected: this is just for plotting purposes

        # For phase signals only: offset, phase check, early jump corrections
        # Early jumps are not recorded as having been corrected
        if "vib" not in self.signal_type:
            # Find indices corresponding to offset time window
            if self.signal_type.startswith("kg1c"):
                self.offset_time = self.offset_time_kg1c
            elif self.signal_type.startswith("kg1r"):
                self.offset_time = self.offset_time_kg1r
            elif self.signal_type.startswith("kg1v"):
                self.offset_time = self.offset_time_kg1v
            else:
                logger.warning("Signal type given {} wasn't recognised.".format(self.signal_type))
                return 10

            logger.log(5, "Offset time window is {}".format(self.offset_time))

            if np.isclose(self.offset_time[0], 0.0, atol=5e-5, rtol=1e-6):
                ind_start = 0
            else:
                ind_start = np.where(self.time >  self.offset_time[0])[0]
                if np.size(ind_start) > 0:
                    ind_start = ind_start[0]
                else:
                    ind_start = 0

            ind_end = np.where(self.time < self.offset_time[1])[0]
            if np.size(ind_end) > 0:
                ind_end = ind_end[-1]
            else:
                logger.debug("Could not find end of offset time window.")
                return 10

            self.offset_time_ind = [ind_start, ind_end]

            # Correct early test jumps
            if signal_type.startswith("kg1c") or signal_type.startswith("kg1r"):
                jumps = self._correct_early_test_jumps()
            else:
                jumps = []

            # Correct the entire trace such that the phase is always 0 at the start
            self._correct_offset()

            # Check the phase isn't completely mad
            phase_ok = self._check_phase()

            if not phase_ok:
                logger.debug("Phase looks dodgy")
                return 10

        if self.constants.plot_type == "dpi" and "signal_kg1" in self.constants.make_plots:
            make_plot([[self.time, self.data]],
                      labels=["{} \n After offset \n & early jump corr".format(signal_name)],
                      xtitles=["time [sec]"], ytitles=["phase"],
                      vert_lines=[jumps], show=True,
                      title="KG1 data {} {}, chan {} before and "\
                            "after correcting for early jumps and offset".format(signal_type, dcn_or_met, chan))

        return 0

    # ------------------------
    def uncorrect_fj(self, corr, index):
        """
        Uncorrect a fringe jump by corr, from the time corresponding to index onwards.
        Not used ATM. Will need more testing if we want to use it... Suspect isclose is wrong.

        :param corr: Correction to add to the data
        :param index: Index from which to make the correction

        """
        # Check we made a correction at this time.
        ind_corr = np.where(np.isclose(self.corrections.time, self.time[index], atol=5e-5, rtol=1e-6) == 1)
        if np.size(ind_corr) == 0:
            return

        # Uncorrect correction
        self.data[index:] = self.data[index:] + corr

        self.corrections.data = np.delete(self.corrections.data, ind_corr)
        self.corrections.time = np.delete(self.corrections.time, ind_corr)

    # ------------------------
    def correct_fj(self, corr, time=None, index=None, store=True, correct_type="", corr_dcn=None, corr_met=None):
        """
        Shifts all data from time onwards, or index onwards,
        down by corr. Either time or index must be specified

        :param corr: The correction to be subtracted
        :param time: The time from which to make the correction (if this is specified index is ignored)
        :param index: The index from which to make the correction
        :param store: To record the correction set to True
        :param correct_type: String describing which part of the code made the correction
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

        logger.log(5, "From index {}, time {}, subtracting {} ({} fringes)".format(index, self.time[index],
                                                                                       corr, corr/self.dfr))
        self.data[index:] = self.data[index:] - corr

        # Store correction in terms of number of fringes
        corr_store = int(corr / self.dfr)

        # If this is a mirror movement signal, store raw correction
        if "vib" in self.signal_type:
            corr_store = corr

        if store:
            # Store in terms of the number of fringes for density, or vibration itself for vibration
            if self.corrections.data is None:
                self.corrections.data = np.array([corr_store])
                self.corrections.time = np.array([self.time[index]])
            else:
                self.corrections.data = np.append(self.corrections.data, corr_store)
                self.corrections.time = np.append(self.corrections.time, self.time[index])

            self.correction_type = np.append(self.correction_type, correct_type)

            # Also store corresponding correction for the DCN & MET lasers (for use with lateral channels only)
            if corr_dcn is not None:
                self.correction_dcn = np.append(self.correction_dcn, corr_dcn)

            if corr_met is not None:
                self.correction_met = np.append(self.correction_met, corr_met)

    # ------------------------
    def sort_corrections(self):
        """
        Sort self.corrections, self.correction_type, self.correction_met
        and self.correct_dcn in time order.
        """
        if self.corrections.data is None:
            return

        ind_sort = np.argsort(self.corrections.time)
        self.corrections.data = self.corrections.data[ind_sort]
        self.corrections.time = self.corrections.time[ind_sort]

        self.correction_type = self.correction_type[ind_sort]

        if len(self.correction_dcn) == len(self.corrections.data):
            self.correction_dcn = self.correction_dcn[ind_sort]

        if len(self.correction_met) == len(self.corrections.data):
            self.correction_met = self.correction_met[ind_sort]

    # ------------------------
    def _reverse_polarity(self):
        """
        Signal polarity was wrong: multiply data by -1.0
        """
        self.data *= -1.0

    # ------------------------
    def _check_phase(self):
        """
        Check the phase isn't bonkers.
        ie. if there is more than an 8*fringe drop in data before the start
        of the plasma, the phase is considered bad.
        """
        phase_diff = (self.data[self.offset_time_ind[1]] - self.data[self.offset_time_ind[0]])

        if (phase_diff / self.dfr) < (-8 * self.constants.fringe):
            logger.log(5, "Phase in offset window drops by > 8*fringe : {}".format(phase_diff / self.dfr))
            return False

        return True

    # ------------------------
    def _correct_early_test_jumps(self):
        """
        Correct test jumps for KG1C, KG1R where fake jumps can be in certain
        locations due to pre-pulse tests in the hardware.

        :return: array of times at which the jumps were corrected

        """
        times_fake_jumps = []

        if self.signal_type == "kg1v":
            return
        elif self.signal_type.startswith("kg1r"):
            # return
            times_fake_jumps = self.KG1R_FAKE_JUMP_TIMES
        elif self.signal_type.startswith("kg1c") and self.dcn_or_met == "dcn":
            times_fake_jumps = self.KG1C_FAKE_JUMP_TIMES_DCN
        elif self.signal_type.startswith("kg1c") and self.dcn_or_met == "met":
            times_fake_jumps = self.KG1C_FAKE_JUMP_TIMES_MET

        if len(times_fake_jumps) == 0:
            return

        phase_before = np.array(self.data)

        phase_diff = self.get_differences(1) / self.dfr

        ind_jumps = [] # For plotting

        # Loop over fake jumps and make corrections
        for jump_time in times_fake_jumps:
            logger.log(5, "Looking for early jump diff at {}".format(jump_time))
            ind_jump, = (np.where(np.isclose(self.time, jump_time, atol=5e-5, rtol=1e-6) == 1))

            if len(ind_jump) > 1:
                continue

            if len(ind_jump) == 0:
                continue

            if ind_jump[0] >= len(phase_diff):
                continue

            # For this correction, we allow non-integer numbers of fringes, since these
            # fake early jumps aren't normally an integer number of fringes
            # Also, don't store the corrections
            self.correct_fj(phase_diff[ind_jump[0]] * self.dfr, index=ind_jump[0]+1, store=False)
            ind_jumps.append(ind_jump[0])

        return self.time[ind_jumps]

    # ------------------------
    def _correct_offset(self):
        """
        First, adjust the offset_time window to ensure it does not
        cover any jumps in the data.
        Then use the average data in the offset_time window
        to ensure the phase at the start of the pulse is 0.
        """

        # Adjust the offset time window to account for any jumps in the data.
        ind_offset = np.where((self.time > self.offset_time[0]) & (self.time < self.offset_time[1]))[0]

        if len(ind_offset) == 0:
            return

        phase_diff = self.get_differences(1)[ind_offset] / self.dfr

        ind_jumps = np.where(np.absolute(phase_diff) > self.constants.fringe)[0] + ind_offset[0]

        if len(ind_jumps) > 0:
            if self.time[ind_jumps[0]] > self.offset_time[0]:
                ind_offset, = np.where((self.time > self.offset_time[0]) & (self.time < self.time[ind_jumps[0]]))
                if len(ind_offset) == 0:
                    return

        # If there is a significant movement of the vessel in the offset time window, adjust
        # the window to cut this movement out.
        if (self.data[ind_offset[-1]] - self.data[ind_offset[0]]) / self.dfr > self.constants.min_fringe:
            ind_small_diff = (np.where((self.data[ind_offset] - self.data[ind_offset[0]]) / self.dfr < 0.1)[0]
                              + ind_offset[0])
            if len(ind_small_diff) > 0:
                ind_offset, = np.where((self.time > self.offset_time[0])
                                      & (self.time < self.time[[np.max(ind_small_diff)]]))

                logger.log(5, "Adjusting offset window due to movement in window.")

                if len(ind_offset) == 0:
                    return


        # Subtract the offset
        offset = np.mean(self.data[ind_offset])

        logger.log(5, "Subtracting offset {}".format(offset))
        if self.pulse >= 92846: # change in firmware: now the offset is computed by the firmware
            logger.log(5, "applying patch due change in firmware: now the offset is computed by the firmware.")

            self.data[ind_offset] = self.data[ind_offset] - offset
        else:
            self.data = self.data - offset


