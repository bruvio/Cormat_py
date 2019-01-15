"""
Class to read and store all kg1 data, and deal
with basic manipulations on it.

Signals are stored in dictionaries, where the key is the channel number
& the value is the appropriate signal class.

Return codes for read_data:

0: Data was read OK
1: Some channels were unavailable for processing.
9: JPF data was unavailable
10: JPF data was bad (eg. amplitude, phase or whatever)
11: All channels have validated PPF data.
66 : Problem reading the geometry file
67 : Failed to write PPF
"""

import logging

import numpy as np

from signal_kg1 import SignalKg1
from signal_amp import SignalAmp
from signal_sts import SignalSTS
from signal_fj import SignalFJ
from signal_base import SignalBase
from kg1_ppf_data import Kg1PPFData
from make_plots import make_plot
from ppf_write import open_ppf, close_ppf, write_ppf
from ppf import ppfgo, ppfuid, ppfget,ppfssr
from ppf import ppfabo
import getdat

logger = logging.getLogger(__name__)

# ----------------------------
__author__ = "L. Kogan"
__version__ = "0.1"

# ----------------------------


class Kg1Data:
    
    # ------------------------
    def __init__(self, constants,pulse):
        """
        Init function

        :param constants: instance of Kg1Consts class
        """
        self.constants = constants
        self.pulse = pulse
        # DCN signal, MET signal
        self.phase_dcn = {}
        self.phase_met = {}

        # LDCOR signals for KG1C (for helping with corrections)
        self.phase_dcn_ldcor = {}
        self.phase_met_ldcor = {}

        # Amplitude signals for DCN & MET
        self.amp_dcn = {}
        self.amp_met = {}

        # For KG1C: 32-bit status flag
        self.kg1c_sts_dcn = {}
        self.kg1c_sts_met = {}

        # For KG1C: FJ signals (number of fringes that were corrected in the LD signals)
        self.kg1c_fj_dcn = {}
        self.kg1c_fj_met = {}

        # Final density and vibration
        self.density = {}
        self.vibration = {}

        # Time dependent status flags
        self.status = {}
        self.global_status = {}

        # PPF data: If a KG1 PPF has already been written,
        # and the status flag of the data is 1,2 or 3
        # (ie. it has already been validated), then
        # this data is just copied over to the output file,
        # no further corrections are made.
        self.ppf = {}

    # ------------------------
    def read_data(self, shot_no, read_uid="JETPPF", ignore_ppf=False):
        """
        Read in KG1 data

        :param shot_no: shot number
        :param read_uid: UID for reading PPF data
        :param ignore_ppf: If this is set to True, then JPF data is read in for correction even if there is already validated KG1V data.
        :returns: 0: Data was read OK,
                  1: Some channels were unavailable for processing,
                  9: JPF data was unavailable,
                  10: JPF data was bad (eg. amplitude, phase or whatever),
                  11: All channels have validated PPF data.

        """
        self.pulse = shot_no
        channels = [1, 2, 3, 4, 5, 6, 7, 8]

        signal_mode = SignalBase(self.constants)

        tried_read_jpf = False

        read_status = 0

        return_code = 0

        if ignore_ppf:
            logger.debug("Testing mode: any KG1R ppf data will be ignored (even if validated already).")

        for chan in channels:
            logger.debug("_______________________________")
            logger.debug("Reading in data for channel {}".format(chan))

            # ------------------
            # First try to read in PPF data for KG1R DDA
            # ------------------
<<<<<<< HEAD
            ppfdata = Kg1PPFData(self.constants)
=======
            ppfdata = Kg1PPFData(self.constants,shot_no)
>>>>>>> savedata
            read_ppf = ppfdata.read_data(shot_no, chan, read_uid=read_uid, all_status=ignore_ppf)

            if read_ppf:
                self.ppf[chan] = ppfdata

                # Only need to read the MODE dtype once (it is the same for all channels)
                if len(self.ppf) == 1:
<<<<<<< HEAD
                    signal_mode.read_data_ppf('KG1R', 'MODE', shot_no, read_bad=False, read_uid=read_uid)
=======
                    signal_mode.read_data_ppf('KG1V', 'MODE', shot_no, read_bad=False, read_uid=read_uid)
>>>>>>> savedata
                    self.ppf[chan].mode = signal_mode.ihdata[36:]
                else:
                    self.ppf[chan].mode = signal_mode.ihdata[36:]

                if not ignore_ppf:
                    continue

<<<<<<< HEAD
            # ------------------
            # If no PPF data (or only un-validated PPF data) was stored for this channel,
            # read in JPF data
            # ------------------
            try:
                signal_type = self.constants.kg1_signal_choices[chan]
            except KeyError:
                logger.debug("Channel {} was not requested in the configuration file.\n".format(chan))
                continue

            tried_read_jpf = True

            if signal_type == "best":
                read_status = max(self._read_best_data(chan, shot_no), read_status)
            else:
                read_status = max(self._read_specific_data(chan, signal_type, shot_no), read_status)
=======

>>>>>>> savedata

            # If any of the channels were unavailable, set return code to 1
            if read_status != 0:
                return_code = 1

            # If channel has been read in, set status flags for entire time trace to 0
            if chan in self.phase_dcn.keys():
                self.status[chan] = SignalBase(self.constants)
                self.status[chan].data = np.zeros(len(self.phase_dcn[chan].time))
                self.status[chan].time = self.phase_dcn[chan].time
                self.global_status[chan] = 0
            if chan in self.phase_met.keys():
                self.status[chan] = SignalBase(self.constants)
                self.status[chan].data = np.zeros(len(self.phase_met[chan].time))
                self.status[chan].time = self.phase_met[chan].time
                self.global_status[chan] = 0
            if chan in self.density.keys() and chan in self.vibration.keys():
                self.status[chan] = SignalBase(self.constants)
                self.status[chan].data = np.zeros(len(self.density[chan].time))
                self.status[chan].time = self.density[chan].time
                self.global_status[chan] = 0

        # ------------------
        # Check if any good signals were found
        # ------------------
        if (len(self.phase_dcn) == 0 and len(self.phase_met) == 0
            and (len(self.density) == 0 or len(self.vibration) == 0)):
            # If didn't even try to read a JPF this means there was validated PPF
            # data for all available channels
            if not tried_read_jpf:
                logger.warning("All channels already have validated PPF data.".format(shot_no))
                return 11

            logger.warning("No good data was found for shot number {}.".format(shot_no))

            # Read status will be 9 if no JPF data was available.
            # It will be 10 if some data was available, but it was bad.
            return read_status

<<<<<<< HEAD
        logger.info("""The following channels have already been validated.
               They will not be reprocessed. {}""".format(self.ppf.keys()))

        logger.info("The following channels will be reprocessed.{}".format(set(self.phase_dcn.keys())
                                                                                | set(self.phase_met.keys())
                                                                                | set(self.density.keys())))

        logger.info("""These channels have DCN data {},
        and these have MET data {},
        and these have density and vibration data (KG1R only!) {}""".format(self.phase_dcn.keys(),
                                                                            self.phase_met.keys(),
                                                                            self.density.keys()))

        return return_code

    # ------------------------
    def _read_best_data(self, chan, shot_no):
        """
        Reads in the signals that are considered to give the best results for each channel.
        For lateral channels use KG1R.
        For vertical channels, use KG1C LD<DCN, if unavailable use KG1C LD<MET.
        Also, read in KG1C LDCOR, FJ & STS variables to help with corrections
        If KG1C is unavailable then use KG1R.

        :param chan: channel number
        :param shot_no: shot number
        :returns: 0 If data was read OK
                 9 if JPF data was unavailable (ie. no DCN AND no MET for KG1C, either no DCN or MET for KG1R)
                 10 if JPF data was bad (ie. bad DCN and MET for KG1C, bad DCN or MET for KG1R)
        """

        logger.log(5, "Reading in the best data for channel {}".format(chan))

        # ------------------
        # If this is a lateral channel, only KG1R data is available,
        # so read this in
        # ------------------
        if chan >= 5:
            return self._read_specific_data(chan, "kg1r", shot_no)

        # ------------------
        # Otherwise, we want to read in KG1C data and ldcor, if available.
        # First, try to read in KG1C LD DCN
        # ------------------
        phase_ld_dcn, amp_dcn, sts_dcn, fj_dcn, read_status_dcn = self._read_one_chan(chan, shot_no, "kg1c_ld", "dcn")

        logger.log(5, "DCN data was read in, read status is {}".format(read_status_dcn))

        if read_status_dcn == 0:
            self.phase_dcn[chan] = phase_ld_dcn
            self.amp_dcn[chan] = amp_dcn
            self.kg1c_sts_dcn[chan] = sts_dcn
            self.kg1c_fj_dcn[chan] = fj_dcn

        # Next, read in KG1C LD MET
        phase_ld_met, amp_met, sts_met, fj_met, read_status_met = self._read_one_chan(chan, shot_no, "kg1c_ld", "met")

        logger.log(5, "MET data was read in, read status is {}".format(read_status_met))

        if read_status_met == 0:
            self.phase_met[chan] = phase_ld_met
            self.amp_met[chan] = amp_met
            self.kg1c_sts_met[chan] = sts_met
            self.kg1c_fj_met[chan] = fj_met

        # If KG1C DCN and MET are unavailable, read in KG1R
        if read_status_dcn != 0 and read_status_met != 0:
            phase_dcn, amp_dcn, sts_dcn, fj_dcn, read_status = self._read_one_chan(chan, shot_no, "kg1r", "dcn")
            if read_status == 0:
                self.phase_dcn[chan] = phase_dcn
                self.amp_dcn[chan] = amp_dcn
            return read_status

        # Otherwise, read in KG1C LDCOR
        if chan in self.phase_dcn.keys():
            phase_node_name = self.constants.get_phase_node_dcn(chan, "kg1c_ldcor")
            phase_ldcor_dcn = SignalKg1(self.constants,shot_no)
            phase_success = phase_ldcor_dcn.read_data_jpf(phase_node_name, shot_no, "kg1c", "dcn", chan, use_64bit=True)

            if phase_success == 0:
                self.phase_dcn_ldcor[chan] = phase_ldcor_dcn

                if self.constants.plot_type == "dpi" and "kg1_data" in self.constants.make_plots:
                    make_plot([[self.phase_dcn[chan].time, self.phase_dcn[chan].data],
                               [self.phase_dcn_ldcor[chan].time, self.phase_dcn_ldcor[chan].data],
                               [self.kg1c_sts_dcn[chan].time, self.kg1c_sts_dcn[chan].ld_valid],
                               [self.kg1c_sts_dcn[chan].time, self.kg1c_sts_dcn[chan].ldcor_valid],
                               [self.kg1c_sts_dcn[chan].time, self.kg1c_sts_dcn[chan].fj_valid],
                               [self.amp_dcn[chan].time, self.amp_dcn[chan].data]],
                               colours=["green","red","red","green","blue","purple"],
                               labels=["phase dcn","phase ldcor dcn","LD valid","LDCOR valid","FJ","amp dcn"],
                               pformat=[2,3,1], show=True,
                               title="After reading in: DCN phase and related signals. Chan {}".format(chan))

        if chan in self.phase_met.keys():
            phase_node_name = self.constants.get_phase_node_met(chan, "kg1c_ldcor")
            phase_ldcor_met = SignalKg1(self.constants,shot_no)
            phase_success = phase_ldcor_met.read_data_jpf(phase_node_name, shot_no, "kg1c", "met", chan, use_64bit=True)
            if phase_success:
                self.phase_met_ldcor[chan] = phase_ldcor_met

                if self.constants.plot_type == "dpi" and "kg1_data" in self.constants.make_plots:
                    make_plot([[self.phase_met[chan].time, self.phase_met[chan].data],
                               [self.phase_met_ldcor[chan].time, self.phase_met_ldcor[chan].data],
                               [self.kg1c_sts_met[chan].time, self.kg1c_sts_met[chan].ld_valid],
                               [self.kg1c_sts_met[chan].time, self.kg1c_sts_met[chan].ldcor_valid],
                               [self.kg1c_sts_met[chan].time, self.kg1c_sts_met[chan].fj_valid],
                               [self.amp_met[chan].time, self.amp_met[chan].data]],
                               colours=["green","red","red","green","blue", "purple"],
                               labels=["phase met","phase ldcor met","LD valid","LDCOR valid","FJ","amp met"],
                               pformat=[2,3,1], show=True,
                               title="After reading in: MET phase and related signals. Chan {}".format(chan))

        # Combine LD and LDCOR
        if chan in self.phase_dcn.keys() and chan in self.phase_dcn_ldcor.keys() and chan in self.kg1c_sts_dcn.keys():
            self._combine_ld_ldcor(self.phase_dcn[chan], self.phase_dcn_ldcor[chan], self.kg1c_sts_dcn[chan])
        if chan in self.phase_met.keys() and chan in self.phase_met_ldcor.keys() and chan in self.kg1c_sts_met.keys():
            self._combine_ld_ldcor(self.phase_met[chan], self.phase_met_ldcor[chan], self.kg1c_sts_met[chan])

        if read_status_dcn != 0 and read_status_met != 0:
            return max(read_status_dcn, read_status_met)

        return 0

    # ------------------------
    def _read_specific_data(self, chan, signal_type, shot_no):
        """
        For a given channel, read in phase and amplitude
        data of type specified. If available also read in STS & FJ signals (KG1C only).
        For the lateral channels, try to read in DCN & MET phases, if not available & KG1R
        was asked for, try to read in density & vibration signals.
        Stores valid signals in the appropriate dictionaries.

        :param chan: channel number
        :param signal_type: Signal type as set in the configuration file.
                    Can be "kg1r", "kg1c_ld", "kg1c_ldraw", "kg1c_ldcor",
                    "kg1c_ld_met", "kg1c_ldraw_met", "kg1c_ldcor_met",
                    "kg1c_ld_dcn", "kg1c_ldraw_dcn", "kg1c_ldcor_dcn",
                    "kg1v"
        :param shot_no: shot number
        """
        logger.log(5, "Read in specific data {} for channel {} and shot_no {}.".format(signal_type, chan, shot_no))

        # For the lateral channels, must have dcn and met
        # For the vertical channels, MET is only available
        # for kg1c, but it is not essential if DCN is available.
        phase_dcn = None
        amp_dcn = None
        phase_met = None
        amp_met = None

        # Require both lasers for lateral channels

        # Read in DCN phase and amplitude
        # Always want to read in DCN (unless they have specifically only asked for met)
        if not signal_type.endswith("_met"):
            ind_end = signal_type.rfind("_dcn")
            if ind_end == -1:
                ind_end = len(signal_type)
            logger.log(5, "Read in DCN data.")
            phase_dcn, amp_dcn, sts_dcn, fj_dcn, read_status_dcn = self._read_one_chan(chan, shot_no,
                                                                                       signal_type[:ind_end], "dcn")

            if self.constants.plot_type == "dpi" and "kg1_data" in self.constants.make_plots and read_status_dcn == 0:
                make_plot([[phase_dcn.time, phase_dcn.data], [amp_dcn.time, amp_dcn.data]],
                          colours=["blue"]*2, labels=["DCN phase {}".format(signal_type), "DCN amp"],
                          pformat=[1,1], show=True,
                          title="After reading: DCN phase {}, chan {}".format(signal_type, chan))

        else:
            read_status_dcn = 9

        # Read in MET phase and amplitude
        # Read in MET (unless they have specifically asked only for dcn)
        if not signal_type.endswith("_dcn") or chan >= 5:
            ind_end = signal_type.rfind("_met")
            if ind_end == -1:
                ind_end = len(signal_type)
            logger.log(5, "Read in MET data.")
            phase_met, amp_met, sts_met, fj_met, read_status_met = self._read_one_chan(chan, shot_no,
                                                                                       signal_type[:ind_end], "met")

            if self.constants.plot_type == "dpi" and "kg1_data" in self.constants.make_plots and read_status_met == 0:
                make_plot([[phase_met.time, phase_met.data], [amp_met.time, amp_met.data]],
                          colours=["blue"]*2, labels=["MET phase {}".format(signal_type), "MET amp"],
                          pformat=[1,1], show=True,
                          title="After reading: MET phase {}, chan {}".format(signal_type, chan))
        else:
            read_status_met = 9

        # Check if valid signal(s) were found.
        # For lateral channels, require both DCN & MET are found.
        # If they have asked for KG1R & DCN & MET were not found (or not requested),
        # read in density & vibration signals.
        # Return status of reading data
        if ((read_status_met != 0 and read_status_dcn != 0)
            or (chan >=5 and (read_status_met != 0 or read_status_dcn != 0))):
            # Will return 9 if both dcn & met JPF were unavailable OR if either were unavailable for lateral chans
            # Will return 10 if dcn & met were bad OR either were bad for lateral chans

            # For KG1R, if the individual phases are not available, we can start from the density & vibration
            if chan >= 5 and signal_type == "kg1r" and amp_dcn is not None and amp_met is not None:
                node_name_ne = self.constants.kg1r_ne[chan]
                ne = SignalKg1(self.constants,shot_no)
                ne_success = ne.read_data_jpf(node_name_ne, shot_no, "kg1r_ne", "dcnmet", chan, use_64bit=True)

                logger.log(5, "KG1R Ne data read status: {}".format(ne_success))

                if ne_success != 0:
                    return max(read_status_met, read_status_dcn, ne_success)

                node_name_vib = self.constants.kg1r_vib[chan]
                vib = SignalKg1(self.constants,shot_no)
                vib_success = vib.read_data_jpf(node_name_vib, shot_no, "kg1r_vib", "dcnmet", chan)

                logger.log(5, "KG1R Vib read status: {}".format(vib_success))

                if vib_success != 0:
                    return max(read_status_met, read_status_dcn, vib_success)

                # KG1R vib needs to be halved, to account for double passage of laser through plasma
                vib.data = vib.data / 2.0

                self.density[chan] = ne
                self.vibration[chan] = vib

                if self.constants.plot_type == "dpi" and "kg1_data" in self.constants.make_plots:
                    make_plot([[self.density[chan].time, self.density[chan].data],
                               [self.vibration[chan].time, self.vibration[chan].data]],
                              colours=["blue"]*2, labels=["density", "vibration"],
                              pformat=[1,1], show=True,
                              title="After reading: Density & Vibration KG1R Chan {}".format(chan))
            else:
                return max(read_status_met, read_status_dcn)

        # Store phases and amplitudes
        if phase_dcn is not None:
            self.phase_dcn[chan] = phase_dcn
        if amp_dcn is not None:
            self.amp_dcn[chan] = amp_dcn
        if phase_met is not None:
            self.phase_met[chan] = phase_met
        if amp_met is not None:
            self.amp_met[chan] = amp_met
        if fj_dcn is not None:
            self.kg1c_fj_dcn[chan] = fj_dcn
        if fj_met is not None:
            self.kg1c_fj_met[chan] = fj_met

        return 0

    # ------------------------
    def _read_one_chan(self, chan, shot_no, signal_type, dcn_or_met):
        """
        Read in phase and amplitude for one channel, and one signal type. If available (KG1C) read in FJ & STS signals.

        :param chan: channel number
        :param shot_no: shot number
        :param signal_type: "kg1r", "kg1c_ld", "kg1c_ldraw", "kg1c_ldcor", "kg1v"
        :param dcn_or_met: "dcn" or "met"
        :return: phase (SignalKg1) , amplitude (SignalAmp),
                 sts (SignalSTS), read_status (0 = good, 9 = no JPF, 10 = JPF read but data bad)
        """

        # KG1C,  KG1R or KG1V ?
        signal_category = "kg1c"
        if signal_type.startswith("kg1r"):
            signal_category = "kg1r"
        if signal_type.startswith("kg1v"):
            signal_category = "kg1v"

        # Get signal names
        if dcn_or_met == "dcn":
            phase_node_name = self.constants.get_phase_node_dcn(chan, signal_type)
            amp_node_name = self.constants.get_amp_node_dcn(chan, signal_type)
            sts_node_name = self.constants.get_sts_node_dcn(chan, signal_type)
            fj_node_name = self.constants.get_fj_node_dcn(chan, signal_type)
        else:
            phase_node_name = self.constants.get_phase_node_met(chan, signal_type)
            amp_node_name = self.constants.get_amp_node_met(chan, signal_type)
            sts_node_name = self.constants.get_sts_node_met(chan, signal_type)
            fj_node_name = self.constants.get_fj_node_met(chan, signal_type)

        if phase_node_name == "" and amp_node_name == "":
            logger.debug("The node names were not found for {} and chan {}".format(signal_type, chan))
            return None, None, None, None, 9

        if sts_node_name == "" and signal_category == "kg1c":
            logger.debug("The STS node name could not be found for {} and chan {}".format(signal_type, chan))
            return None, None, None, None, 9

        if fj_node_name == "" and signal_category == "kg1c":
            logger.debug("The FJ node name could not be found for {} and chan {}".format(signal_type, chan))
            return None, None, None, None, 9

        logger.log(5, "Read phase {} and amp {}".format(phase_node_name, amp_node_name))

        # Read in amplitude
        amp = SignalAmp(self.constants)
        amp_success = amp.read_data_jpf(amp_node_name, shot_no, signal_category, dcn_or_met)
        logger.log(5, "Amp return code? {}".format(amp_success))

        if amp_success != 0:
            return None, None, None, None, amp_success

        # Read in phase
        phase = SignalKg1(self.constants,shot_no)
        phase_success = phase.read_data_jpf(phase_node_name, shot_no, signal_category, dcn_or_met, chan, use_64bit=True)
        logger.log(5, "Phase return code? {}".format(phase_success))

        if phase_success != 0:
            return None, amp, None, None, phase_success

        # For KG1C, read in STS (32-bit status flag)
        sts = None
        if signal_category == "kg1c" and sts_node_name != "":
            sts = SignalSTS(self.constants)
            sts_success = sts.read_data_jpf(sts_node_name, shot_no, dcn_or_met)
            if not sts_success:
                return None, None, None, None, 9

        # For KG1C, read in FJ
        fj = None
        if signal_category == "kg1c" and fj_node_name != "":
            fj = SignalFJ(self.constants, phase)
            fj_success = fj.read_data_jpf(fj_node_name, shot_no)

            if not fj_success:
                return None, None, None, None, 9

        return phase, amp, sts, fj, 0

    # ------------------------
    def _combine_ld_ldcor(self, phase_ld, phase_ldcor, sts):
        """
        This function checks for points in ld which are invalid,
        but where ldcor is valid, and replaces ld with ldcor

        NB: SOMETIMES THIS DOESN'T WORK... SOMETIMES PHASE IS SET
        TO 0 IN JPF, BUT LD STS FLAG IS GOOD, SO REPLACEMENT IS NOT MADE.
        OR : LDCOR PHASE IS SET TO 0 (OR EVEN WORSE SOMETHING NOT ZERO)
        BUT LDCOR STS FLAG IS GOOD... THIS
        CAN CAUSE SOME NASTY FAKE JUMPS... BUT IN GENERAL THIS ONLY
        HAPPENS WHEN DATA IS UNRETRIEVABLE ANYWAY... NEEDS TO BE CHECKED.

        :param phase_ld: ld phase
        :param phase_ldcor: ldcor phase
        :param sts: SignalSTS, which contains ldvalid and ldcor valid status flags
        """

        # Can replace LD with LDCOR where LDCOR is valid, but LD is invalid.
        # Have to additionally make sure LDCOR phase is not zero (sometimes it
        # is set to zero, but the STS flag is 1).
        # Also need to be careful when LDCOR goes from invalid to valid and vice-versa,
        # can't use differences at these boundaries.
        ldcor_valid = sts.ldcor_valid * np.array(phase_ldcor.data > 0, dtype=int)
        ldcor_valid_diff = ldcor_valid[1:] - ldcor_valid[0:-1]
        ldcor_valid_diff = np.append(ldcor_valid_diff, 1)

        # Find indices where swap should be made
        swap_ld_ldcor = (sts.ld_valid == 0) & (sts.ldcor_valid == 1) & (ldcor_valid_diff == 0)
        ind_swap = np.where(swap_ld_ldcor == True)

        if len(ind_swap[0]) == 0:
            return

        # Replace sections using differences and then taking cumulative sum (avoids loop)
        # TO DO: Check speed vs loop... if loop is faster use that
        phase_ld_diff = phase_ld.get_differences(1)
        phase_ldcor_diff = phase_ldcor.get_differences(1)

        phase_ld_diff[ind_swap] = phase_ldcor_diff[ind_swap]

        new_data = np.cumsum(phase_ld_diff)
        # Make sure to add the first data point back in
        new_data = np.insert(new_data, 0, phase_ld.data[0])

        if self.constants.plot_type == "dpi" and "kg1_data" in self.constants.make_plots:
            make_plot([[phase_ld.time, phase_ld.data], [phase_ld.time, new_data]],
                      colours=["blue", "red"], labels=["before", "after"], show=True,
                      pformat=[2])

        phase_ld.data = new_data
=======


        return return_code


>>>>>>> savedata

    # ------------------------
    def set_status(self, lid, new_status, time=None, index=None):
        """
        Set time-dependent status flags for lid.

        If neither time or index are given, set status flags for all time points

        :param lid: LID number to set status for
        :param new_status: status to be set
        :param time: time, or time range in which to set status.
        :param index: index, or index range in which to set status.
        """
        if lid not in self.status.keys() or new_status < 0 or new_status > 4:
            return

        # Set status for all time points
        if time is None and index is None:
            self.status[lid].data[:] = new_status
            return

        # Find indices to set from time
        if time is not None and len(time) == 1:
            index = np.where(np.isclose(self.status[lid].time, time, atol=0.00005, rtol=1e-6))[0]
        elif time is not None and len(time) == 2:
            index = [(np.abs(self.status[lid].time - time[0])).argmin(),
                     (np.abs(self.status[lid].time - time[1])).argmin()]

        # Set status flags
        if index is not None:
            if len(index) == 2:
                self.status[lid].data[index[0]:index[1]] = new_status
                logger.debug("Chan {}: Setting status to {} between {}-{}".format(lid, new_status,
                                                                                      self.status[lid].time[index[0]],
                                                                                      self.status[lid].time[index[1]]))
            else:
                self.status[lid].data[index] = new_status
                logger.debug("Chan {}: Setting status to {} for time point {}".format(lid, new_status,
                                                                                   self.status[lid].time[index]))

    # ------------------------
    def get_jpf_point(self, shot_no, node):
        """
        Get a single value from the JPF
        ie. Convert Nord data to real number
        Function copied from A. Boboc's kg4r_py code.

        :param shot_no: shot number
        :param node: JPF node
        """
        (raw,nwords,label,ecode) = getdat.getraw(node,shot_no)
        t = None
        if ecode != 0:
            logger.warning("{} {} BAD".format(shot_no, node))
        else:
            if nwords == 3:
                # Data is 3 16bit words Nord float, 48 bit
                # word 0, bit 0 is sign
                # word 0, bit 1..15 is exponent, biased
                # word 1, bit 0..15 is most significant mantissa
                # word 2, bit 0..15 is least significant mantissa
                w0 = raw[0] & 0xffff
                w1 = raw[1] & 0xffff
                w2 = raw[2] & 0xffff
                if w0 & 0x8000 : # sign
                    s = -1.0
                else:
                    s =  1.0
                e = w0 & 0x7fff # exponent
                eb = 0x4000 # exponent bias
                #print jpn, node, w0, w1, w2,
                msm = w1<<8  # most significant mantissa for IEE754 float, 32 bit
                lsm = w2>>8  # least significant mantissa
                mm = 0x1000000 # mantissa max
                fm = float(msm+lsm)
                fmm = float(mm)
                if (e) != 0:
                    t = s * (2**(e-eb)) * (fm/fmm)
                else:
                    t= 0.0
                #Debug_msg(1,'Pulse' +str(jpn)+node+' '+t)
        return (t,ecode)


    # ------------------------
    def get_coord(self, shot_no):
        """
        Get vacuum vessel temperature & extract spatial coordinates of KG4 chords from text file.
        Function copied from A. Boboc's kg4r_py code.

        :param shot_no: shot number
        """

        nodename_temp = self.constants.temp_node

        vv_temp, err = self.get_jpf_point(shot_no, nodename_temp)

        filename = self.constants.geometry_filename

        try:
            raw = np.loadtxt(filename, skiprows=3)

            temp = raw[:,0]
            index = np.where(temp==vv_temp)[0]
            Coord_Rref = raw[0,1:9]
            Coord_Zref = raw[0,9:17]
            Coord_Aref = raw[0,17:25]
            Coord_R = raw[index,1:9][0]
            Coord_Z = raw[index,9:17][0]
            Coord_A = raw[index,17:25][0]
            Coord_Temperature = vv_temp

            logger.debug('Vaccum Vessel temperature(deg.C) {}'.format(vv_temp))
            logger.debug('Rref {}'.format(Coord_Rref))
            logger.debug('Zref {}'.format(Coord_Zref))
            logger.debug('Aref {}'.format(Coord_Aref))
            logger.debug('R {}'.format(Coord_R))
            logger.debug('Z {}'.format(Coord_Z))
            logger.debug('A {}'.format(Coord_A))

            return (Coord_Temperature,Coord_R,Coord_Z,\
                    Coord_A,Coord_Rref,Coord_Zref,Coord_Aref,0)

        except IOError:
            pass
            ier = 1
            logger.debug("Reading KG4 R,Z,A coordinates data from {} failed".format(filename))
            return 1,1,1,1,1,1,1,66

    # ------------------------
    def write_data(self, shot_no, write_uid, magnetics, ignore_current_ppf=False,interp_kg1v=False):
        """
        Write data to PPF for KG1V & KG1B DDAs

        :param shot_no: shot number
        :param write_uid: User-ID to use when writing PPFs
        :param magnetics: Instance of MagData. Needed to calculate JxB movement.
        """
        err = open_ppf(shot_no, write_uid)

        if err != 0:
            return 67

        err = self.write_data_kg1r(shot_no, write_uid, magnetics, ignore_current_ppf=ignore_current_ppf,interp_kg1v=interp_kg1v)

        #  Error = 0, no problem, Error == 2: FCXX variables couldn't be written, but rest of DDA was written.
        if err != 0:
            ppfabo()
            return err

        logger.log(5, "Close PPF.")
        err = close_ppf(shot_no, write_uid, self.constants.code_version)

        if err != 0:
            return 67

        return 0

    # ------------------------
    def write_data_kg1b(self, shot_no):
        """
        Write data to PPF for KG1B DDA

        :param shot_no: shot number
        :param write_uid: User-ID to use when writing KG1B PPF

        :returns 0 if everything is OK, 67 otherwise
        """
        dda = "KG1B"
        comment = "DATA FROM KG1 CHANNEL"

        # Write data by channel that has been calculated here
        write_err = self.write_bad_points_all(shot_no, dda, comment)

        if write_err != 0:
            return 67

        return 0

    # ------------------------
    def write_bad_points_all(self, shot_no, dda, comment):
        """
        For all channels, write bad data point signals

        :param shot_no: shot number
        :param dda: DDA
        :param comment: comget_coordment
        """
        for chan in self.density.keys():

            if chan in self.amp_dcn.keys():
                dtype = "BPD{}".format(chan)

                write_err = self.write_bad_points(shot_no, dda, dtype, self.amp_dcn[chan], comment)

                if write_err != 0:
                    logger.info("Failed to write {}/{}. Errorcode {}".format(dda, dtype, write_err))
                    break

            if chan in self.amp_met.keys():
                dtype = "BPM{}".format(chan)

                write_err = self.write_bad_points(shot_no, dda, dtype, self.amp_met[chan], comment)

                if write_err != 0:
                    logger.info("Failed to write {}/{}. Errorcode {}".format(dda, dtype, write_err))
                    break

        if write_err != 0:
            return 67

        return 0

    # ------------------------
    def write_bad_points(self, shot_no, dda, dtype, amp_signal, comment):
        """
        Write points with bad amplitude to DDA/DTYPE

        :param shot_no: shot number
        :param dda: DDA
        :param dtype: DTYPE
        :param amp_signal: Instance of SignalAmp
        :param comment: comment
        :return: 0 if everything is OK
        """
        write_err = 0

        ind_bad = amp_signal.find_bad_points()

        if len(ind_bad) > 0:
            time_bad = amp_signal.time[ind_bad]

            data_bad = np.arange(len(time_bad)) + 1

            write_err, itref_written = write_ppf(shot_no, dda, dtype, data_bad,
                                                 time=time_bad, comment=comment,
                                                 unitd='M-2', unitt='SEC', itref=-1,
                                                 nt=len(time_bad))

        return write_err

    # ------------------------
    def write_data_kg1r(self, shot_no, write_uid, magnetics, ignore_current_ppf=False,interp_kg1v=False):
        """
        Write data to PPF for KG1R DDA

        :param shot_no: shot number
        :param write_uid: User-ID to use when writing KG1R PPF
        :param magnetics: Instance of MagData. Needed to calculate JxB movement.

        :returns 0 if everything is OK, 67 otherwise
        """
        dda = "KG1R"
        if interp_kg1v:
        # if we interp then we write as KG1V dda to read the ppf in Cormat
            dda = "KG1V"

        itref_kg1c = -1
        itref_kg1r = -1
        itref_kg1v = -1

        write_err = 0

        mag_bvac = magnetics.bvac
        eddy_current = magnetics.eddy_current

        return_code = 0
        if interp_kg1v:
            # temporary solution
            # interp kg1 data into kg1v time base
            # a particular shot has to be selected (that exists!)
            # moreover the question is what to do with the fast sampling window
            # the DC sets in the control room
            # how to access this information?
            logger.info("_______________________________")
            logger.info("Reading in KG1V data ")
            ier = ppfgo('92025', seq=0)

            ppfuid('jetppf', rw="R")

            if ier != 0:
                return 0

            ihdata_kg1v, iwdata_kg1v, data_kg1v, x_kg1v, time_kg1v, ier_kg1v = ppfget('92025', 'KG1V', 'LID3')
        # Write data by channel that has been calculated here
        for chan in self.density.keys():
            import pdb
            # pdb.set_trace()

            logger.debug("-------------------------------")
            logger.debug("Writing new data for channel {}".format(chan))

            # If we have already written a channel with a specific type of data, we want to
            # share the time-axis rather than re-write it. So, pick the appropriate itref
            # Assumes all channels with the same type of data have the same timebase.
            if self.density[chan].signal_type.startswith("kg1c"):
                itref = itref_kg1c
            elif self.density[chan].signal_type.startswith("kg1r"):
                itref = itref_kg1r
            else:
                itref = itref_kg1v
            if interp_kg1v:
            # temporary solution
            # interp kg1 data into kg1v time base
            # a particular shot has to be selected (that exists!)
            # moreover the question is what to do with the fast sampling window
            # the DC sets in the control room
            # how to access this information?
                logger.info("temporary solution resampling channel {} to use CORMAT with KG1R".format(chan))
                self.density[chan].data, self.density[chan].time = \
                self.density[chan].resample_signal("zeropadding", time_kg1v)
            # LID data
            dtype_lid = "LID{}".format(chan)
            comment = "DATA FROM KG1 CHANNEL {}".format(chan)
            write_err, itref_written = write_ppf(shot_no, dda, dtype_lid, self.density[chan].data,
                                                 time=self.density[chan].time, comment=comment,
                                                 unitd='M-2', unitt='SEC', itref=itref,
                                                 nt=len(self.density[chan].time), status=self.status[chan].data,
                                                 global_status=self.global_status[chan])

            # Store the itref in the appropriate variable according to signal type
            if self.density[chan].signal_type.startswith("kg1c") and itref == -1:
                itref_kg1c = itref_written
            elif self.density[chan].signal_type.startswith("kg1r") and itref == -1:
                itref_kg1r = itref_written
            elif itref == -1:
                itref_kg1v = itref_written
            # test
            # if itref
            # -1	A new vector is to be written
            # 0	No vector is to be written
            # >0	A previously stored x-/t-vector, whose reference number is supplied here, is to be used by this DataType.
            # bypassing update of itref

            itref = itref_written

            if write_err != 0:
                logger.error("Failed to write {}/{}. Errorcode {}".format(dda, dtype_lid, write_err))
                break

            # Corrected FJs for vertical channels
            if chan <= 4 and self.density[chan].corrections.data is not None:
                self.density[chan].sort_corrections()

                # dtype_fc = "FCD{}".format(chan)
                dtype_fc = "FC{} ".format(chan)
                comment = "DCN FRINGE CORR CH.{}".format(chan)

                if self.density[chan].dcn_or_met == "met":
                    # dtype_fc = "FCM{}".format(chan)
                    dtype_fc = "MC{} ".format(chan)
                    comment = "MET FRINGE CORR CH.{}".format(chan)

                write_err, itref_written = write_ppf(shot_no, dda, dtype_fc, self.density[chan].corrections.data,
                                                    time=self.density[chan].corrections.time, comment=comment,
                                                    unitd=" ", unitt="SEC", itref=-1,
                                                    nt=len(self.density[chan].corrections.time), status=None)

                if write_err != 0:
                    logger.error("Failed to write {}/{}. Errorcode {}".format(dda, dtype_fc, write_err))
                    break

            # Vibration data and JXB for lateral channels, and corrected FJ
            elif chan > 4 and chan in self.vibration.keys():
                # Vibration
                dtype_vib = "MIR{}".format(chan)
                comment = "MOVEMENT OF MIRROR {}".format(chan)
                if interp_kg1v:
                    # temporary solution
                    # interp kg1 data into kg1v time base
                    # a particular shot has to be selected (that exists!)
                    # moreover the question is what to do with the fast sampling window
                    # the DC sets in the control room
                    # how to access this information?                    
                    self.vibration[chan].data, self.vibration[chan].time = self.vibration[chan].resample_signal("zeropadding", time_kg1v)
                write_err, itref_written = write_ppf(shot_no, dda, dtype_vib, self.vibration[chan].data,
                                                     time=self.vibration[chan].time, comment=comment,
                                                     unitd='M', unitt='SEC', itref=itref,
                                                     nt=len(self.vibration[chan].time), status=self.status[chan].data,
                                                     global_status=self.global_status[chan])
                if write_err != 0:
                    logger.error("Failed to write {}/{}. Errorcode {}".format(dda, dtype_vib, write_err))
                    break

                # JXB movement
                # (no need to decimate it as it is already linked to density timebase)
                dtype_jxb = "JXB{}".format(chan)
                comment = "JxB CALC. MOVEMENT CH.{}".format(chan)
                bvac_here = mag_bvac.resample_signal("interp", self.density[chan].time)
                eddy_here = eddy_current.resample_signal("interp", self.density[chan].time)
                jxb_data = -1.0 * self.constants.JXB_FAC[chan-5] * eddy_here * bvac_here


                write_err, itref_written = write_ppf(shot_no, dda, dtype_jxb, jxb_data,
                                                     time=self.density[chan].time, comment=comment,
                                                     unitd="M", unitt="SEC", itref=itref,
                                                     nt=len(self.density[chan].time), status=None)

                # Corrections to density and vibration : store in terms of FJ corrections in DCN & MET
                if self.density[chan].corrections.data is not None:
                    self.density[chan].sort_corrections()
                    dtype_fc = "FC{} ".format(chan)
                    if len(self.density[chan].correction_dcn) == len(self.density[chan].corrections.data):
                        # dtype_fc = "FCD{}".format(chan)

                        comment = "DCN FRINGE CORR CH.{}".format(chan)

                        write_err, itref_written = write_ppf(shot_no, dda, dtype_fc, self.density[chan].correction_dcn,
                                                    time=self.density[chan].corrections.time, comment=comment,
                                                    unitd=" ", unitt="SEC", itref=-1,
                                                    nt=len(self.density[chan].corrections.time), status=None)
                    else:
                        logger.error("Failed to write {}/{}. Errorcode {}".format(dda, dtype_fc, write_err))
                        break

                if self.vibration[chan].corrections.data is not None:
                    self.vibration[chan].sort_corrections()
                    dtype_fc = "MC{} ".format(chan)
                    if len(self.vibration[chan].correction_met) == len(self.vibration[chan].corrections.data):
                        # dtype_fc = "FCM{}".format(chan)

                        comment = "MET FRINGE CORR CH.{}".format(chan)

                        write_err, itref_written = write_ppf(shot_no, dda, dtype_fc,
                                                             self.vibration[chan].correction_met,
                                                    time=self.vibration[chan].corrections.time, comment=comment,
                                                    unitd=" ", unitt="SEC", itref=-1,
                                                    nt=len(self.vibration[chan].corrections.time), status=None)
                    else:
                        logger.error("Failed to write {}/{}. Errorcode {}".format(dda, dtype_fc, write_err))
                        break

            itref = -1

            # Write signal type
            dtype_type = "TYP{}".format(chan)
            comment = "SIG TYPE: {} CH.{}".format(self.density[chan].signal_type, chan)
            write_err, itref_written = write_ppf(shot_no, dda, dtype_type, np.array([1]),
                                                 time=np.array([0]), comment=comment, unitd=" ", unitt=" ", itref=-1,
                                                 nt=1, status=None)

            mode = "Automatic Corrections"
        if write_err != 0:
            return 67

        # Bad points as part of the KG1R PPF: commented out at the moment
        # comment_bad = "Points with bad amplitude"
        # write_err = self.write_bad_points_all(shot_no, dda, comment_bad)
        # if write_err != 0:
        #    return 67

        # Write data by channel that has been read from PPF
        if not ignore_current_ppf:
            ppf_type_map = {}

            for chan in self.ppf.keys():
                if self.ppf[chan].density.data is None:
                    continue

                logger.debug("-------------------------------")
                logger.debug("Copying PPF data for channel {}".format(chan))

                if self.ppf[chan].type in ppf_type_map.keys():
                    itref = ppf_type_map[self.ppf[chan].type]

                write_err, itref_written = self.ppf[chan].write_data(chan, shot_no, itref)

                if write_err != 0:
                    logger.error("Failed to write validated PPF data for channel {}".format(chan))
                    break

                if self.ppf[chan].type not in ppf_type_map.keys():
                    ppf_type_map[self.ppf[chan].type] = itref_written

                mode = self.ppf[chan].mode

            if write_err != 0:
                return 67

        # Retrieve geometry data & write to PPF
        temp, r_ref, z_ref, a_ref, r_coord, z_coord, a_coord, coord_err = self.get_coord(shot_no)

        if coord_err != 0:
            return coord_err

        dtype_temp = "TEMP"
        comment = "Vessel temperature(degC)"
        write_err, itref_written = write_ppf(shot_no, dda, dtype_temp, np.array([temp]),
                                             time=np.array([0]), comment=comment, unitd="deg", unitt="none",
                                             itref=-1, nt=1, status=None)

        geom_chan = np.arange(len(a_ref)) + 1
        dtype_aref = "AREF"
        comment = "CHORD(20 DEC.C): ANGLE"
        write_err, itref_written = write_ppf(shot_no, dda, dtype_aref, a_ref,
                                             time=geom_chan, comment=comment, unitd="RADIANS", unitt="CHORD NO",
                                             itref=-1, nt=len(geom_chan), status=None)

        dtype_rref = "RREF"
        comment = "CHORD(20 DEC.C): RADIUS"
        write_err, itref_written = write_ppf(shot_no, dda, dtype_rref, r_ref,
                                             time=geom_chan, comment=comment, unitd="M", unitt="CHORD NO",
                                             itref=itref_written, nt=len(geom_chan), status=None)

        dtype_zref = "ZREF"
        comment = "CHORD(20 DEC.C): HEIGHT"
        write_err, itref_written = write_ppf(shot_no, dda, dtype_zref, z_ref,
                                             time=geom_chan, comment=comment, unitd="M", unitt="CHORD NO",
                                             itref=itref_written, nt=len(geom_chan), status=None)

        dtype_a = "A   "
        comment = "CHORD: ANGLE"
        write_err, itref_written = write_ppf(shot_no, dda, dtype_a, a_coord,
                                             time=geom_chan, comment=comment, unitd="RADIANS", unitt="CHORD NO",
                                             itref=itref_written, nt=len(geom_chan), status=None)

        dtype_r = "R   "
        comment = "CHORD: RADIUS"
        write_err, itref_written = write_ppf(shot_no, dda, dtype_r, r_coord,
                                             time=geom_chan, comment=comment, unitd="M", unitt="CHORD NO",
                                             itref=itref_written, nt=len(geom_chan), status=None)

        dtype_z = "Z   "
        comment = "CHORD: HEIGHT"
        write_err, itref_written = write_ppf(shot_no, dda, dtype_z, z_coord,
                                             time=geom_chan, comment=comment, unitd="M", unitt="CHORD NO",
                                             itref=itref_written, nt=len(geom_chan), status=None)

        # Write mode DDA
        dtype_mode = "MODE"
        comment = mode
        write_err, itref_written = write_ppf(shot_no, dda, dtype_mode, np.array([1]), time=np.array([0]),
                                             comment=comment, unitd=" ", unitt=" ", itref=-1, nt=1, status=None)

        return return_code
