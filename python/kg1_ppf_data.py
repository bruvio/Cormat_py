"""
Class to read and store KG1 PPF data for one channel.
Reads in LIDX, FCX, MIRX, JXBX, TYPX

"""

import logging
import getdat
import numpy as np
from ppf_write import write_ppf
from signal_kg1 import SignalKg1
from signal_base import SignalBase
from pdb import set_trace as bp

logger = logging.getLogger(__name__)

# ----------------------------
__author__ = "B. Viola"
# ----------------------------


class Kg1PPFData(SignalBase):

    # ------------------------
    def __init__(self, constants,pulse):
        """
        Init function
        :param constants: instance of Kg1Consts class
        """
        # self.signal_type = ""  # kg1r, kg1c, kg1v
        # self.dcn_or_met = "" # dcn, met

        self.constants = constants
        self.pulse = pulse
        self.dda = "KG1V"
        self.density = {}
        self.vibration = {}
        self.fj_dcn = {}
        self.fj_met = {}
        self.jxb = {}

        # Time dependent status flags
        self.status = {}
        self.global_status = {}
        self.kg1rt = {}
        self.type = {}
        self.mode = ""

        # PPF data: If a KG1 PPF has already been written,
        # and the status flag of the data is 1,2 or 3
        # (ie. it has already been validated), then
        # this data is just copied over to the output file,
        # no further corrections are made.
        self.ppf = {}

        self.dfr = self.constants.DFR_DCN

    # ------------------------
    def read_data(self, shot_no, read_uid="JETPPF"):
        """
        Read in PPF data for KG1V for a given channel
        :param shot_no: shot number
        :param chan: channel
        :param read_uid: read UID
        :return: True if data was read in successfully, False otherwise
        """
        for chan in self.constants.kg1v.keys():
            nodename = self.constants.kg1v[chan]
            density = SignalKg1(self.constants,self.pulse)
            # corrections = SignalBase(self.constants)
            dda = nodename[:nodename.find('/')]
            dtype = nodename[nodename.find('/')+1:]
            status = density.read_data_ppf(dda, dtype, shot_no, read_bad=True, read_uid=read_uid)

            # We are only interested in keeping the data if it has already been validated
            # if density.data is not None and (0 < status < 4) and not all_status:
            #     logger.debug( "PPF data chan {}".format(status))
            if density.data is not None:
                self.density[chan] = density
                self.status[chan] = SignalBase(self.constants)
                self.status[chan].data = np.zeros(
                        len(self.density[chan].time))
                self.status[chan].time = self.density[chan].time
                self.global_status[chan] = 0
                # self.density[chan].corrections = SignalBase(self.constants)
                self.density[chan].signal_type = 'vert'
                if chan >4:
                    self.density[chan].signal_type = 'lat'
                    self.density[chan].correction_dcn = SignalBase(self.constants)
                    self.density[chan].correction_met = SignalBase(self.constants)

            # else:
            #     return False
            # else:
            #     return False

        for chan in self.constants.kg1rt.keys():
            node_name = self.constants.kg1rt[chan]
            kg1rt_signal = SignalBase(self.constants)
            kg1rt_signal.read_data_jpf(node_name, shot_no)
            if kg1rt_signal.data is not None:
                self.kg1rt[chan] = kg1rt_signal



        for chan in self.constants.kg1r_ppf_vib.keys():
            nodename = self.constants.kg1r_ppf_vib[chan]
            vibration = SignalKg1(self.constants,self.pulse)
            dda = nodename[:nodename.find('/')]
            dtype = nodename[nodename.find('/')+1:]
            status = vibration.read_data_ppf(dda, dtype, shot_no, read_bad=True, read_uid=read_uid)

            if vibration.data is not None:
                self.vibration[chan] = vibration
                self.vibration[chan].signal_type = 'lat'
                self.status[chan] = SignalBase(self.constants)
                self.status[chan].data = np.zeros(
                        len(self.density[chan].time))
                self.status[chan].time = self.density[chan].time
                self.global_status[chan] = 0
                self.vibration[chan].corrections = SignalBase(self.constants)

        for chan in self.constants.kg1r_ppf_fj_dcn.keys():
            nodename = self.constants.kg1r_ppf_fj_dcn[chan]
            fj = SignalBase(self.constants)

            dda = nodename[:nodename.find('/')]
            dtype = nodename[nodename.find('/')+1:]
            status = fj.read_data_ppf(dda, dtype, shot_no, read_bad=True, read_uid=read_uid)

            if fj.data is not None:
                self.fj_dcn[chan] = fj

        for chan in self.constants.kg1r_ppf_fj_met.keys():
            nodename = self.constants.kg1r_ppf_fj_met[chan]
            fj = SignalBase(self.constants)

            dda = nodename[:nodename.find('/')]
            dtype = nodename[nodename.find('/')+1:]
            status = fj.read_data_ppf(dda, dtype, shot_no, read_bad=True, read_uid=read_uid)

            if fj.data is not None:
                self.fj_met[chan] = fj

        for chan in self.constants.kg1r_ppf_bp_dcn.keys():
            nodename = self.constants.kg1r_ppf_bp_dcn[chan]
            bp = SignalBase(self.constants)

            dda = nodename[:nodename.find('/')]
            dtype = nodename[nodename.find('/')+1:]
            status = bp.read_data_ppf(dda, dtype, shot_no, read_bad=True, read_uid=read_uid)

            if bp.data is not None:
                self.bp_dcn[chan] = bp

        for chan in self.constants.kg1r_ppf_bp_met.keys():
            nodename = self.constants.kg1r_ppf_bp_met[chan]
            bp = SignalBase(self.constants)

            dda = nodename[:nodename.find('/')]
            dtype = nodename[nodename.find('/')+1:]
            status = bp.read_data_ppf(dda, dtype, shot_no, read_bad=True, read_uid=read_uid)

            if bp.data is not None:
                self.bp_met[chan] = bp

        for chan in self.constants.kg1r_ppf_jxb.keys():
            nodename = self.constants.kg1r_ppf_jxb[chan]
            jxb = SignalBase(self.constants)
            dda = nodename[:nodename.find('/')]
            dtype = nodename[nodename.find('/')+1:]
            status = jxb.read_data_ppf(dda, dtype, shot_no, read_bad=True, read_uid=read_uid)

            if jxb.data is not None:
                self.jxb[chan] = jxb

        for chan in self.constants.kg1r_ppf_type.keys():
            nodename = self.constants.kg1r_ppf_type[chan]
            sig_type = SignalBase(self.constants)
            dda = nodename[:nodename.find('/')]
            dtype = nodename[nodename.find('/')+1:]
            status = sig_type.read_data_ppf(dda, dtype, shot_no, read_bad=True, read_uid=read_uid)

            if sig_type.data is not None:
                ind_type = sig_type.ihdata.find("SIG TYPE:")+len("SIG TYPE:")+1
                ind_chan = sig_type.ihdata.find("CH.")-1
                self.type[chan] = sig_type.ihdata[ind_type:ind_chan]
        

        nodename_mode = self.constants.mode

        signal_mode = SignalBase(self.constants)
        
        signal_mode.read_data_ppf('KG1V', 'MODE', shot_no, read_bad=False, read_uid=read_uid)
        try:
            self.mode = signal_mode.ihdata[36:]
        except TypeError:
            logger.error('no KG1V/MODE data!')

        


        
        return True


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


    # # ------------------------
    # def uncorrect_fj(self, corr, index):
    #     """
    #     Uncorrect a fringe jump by corr, from the time corresponding to index onwards.
    #     Not used ATM. Will need more testing if we want to use it... Suspect isclose is wrong.
    #
    #     :param corr: Correction to add to the data
    #     :param index: Index from which to make the correction
    #
    #     """
    #     # Check we made a correction at this time.
    #     ind_corr = np.where(np.isclose(self.corrections.time, self.time[index], atol=5e-5, rtol=1e-6) == 1)
    #     if np.size(ind_corr) == 0:
    #         return
    #
    #     # Uncorrect correction
    #     self.data[index:] = self.data[index:] + corr
    #
    #     self.corrections.data = np.delete(self.corrections.data, ind_corr)
    #     self.corrections.time = np.delete(self.corrections.time, ind_corr)
    #
    # # ------------------------
    # def correct_fj(self, chan, fringe,mirror=None, time=None, index=None, store=True, correct_type="", corr_dcn=None, corr_met=None):
    #     """
    #     Shifts all data from time onwards, or index onwards,
    #     down by corr. Either time or index must be specified
    #
    #     :param corr: The correction to be subtracted
    #     :param time: The time from which to make the correction (if this is specified index is ignored)
    #     :param index: The index from which to make the correction
    #     :param store: To record the correction set to True
    #     :param correct_type: String describing which part of the code made the correction
    #     :param corr_dcn: Only for use with lateral channels. Stores the correction,
    #                      in terms of the number of FJ in DCN laser (as opposed to in the combined density)
    #     :param corr_met: Only for use with lateral channels. Stores the correction,
    #                      in terms of the number of FJ in the MET laser (as opposed to the correction in the vibration)
    #
    #     """
    #     poss_ne_corr = np.array([self.data.constants.CORR_NE]*20) * np.array([np.arange(20)+1]*len(self.data.constants.CORR_NE)).transpose()
    #     poss_vib_corr = np.array([self.data.constants.CORR_VIB]*20) * np.array([np.arange(20)+1]*len(self.data.constants.CORR_VIB)).transpose()
    #     poss_dcn_corr = np.array([self.data.constants.FJ_DCN]*20) * np.array([np.arange(20)+1]*len(self.data.constants.FJ_DCN)).transpose()
    #     poss_met_corr = np.array([self.data.constants.FJ_MET]*20) * np.array([np.arange(20)+1]*len(self.data.constants.FJ_MET)).transpose()
    #
    #
    #     if time is None and index is None:
    #         logger.warning("No time or index was specified for making the FJ correction.")
    #         return
    #
    #     if time is not None:
    #         index = np.where(self.time > time),
    #         if np.size(index) == 0:
    #             logger.warning("Could not find time near {} for making the FJ correction.".format(time))
    #             return
    #
    #         index = np.min(index)
    #
    #     logger.debug( "From index {}, time {}, subtracting {} ({} fringes)".format(index, self.time[index],
    #                                                                                   corr, corr/self.dfr))
    #     corr = fringe * self.dfr
    #
    #     self.density[chan].data[index:] = self.density[chan].data[index:] - corr
    #
    #     # Store correction in terms of number of fringes
    #     # corr_store = int(corr / self.dfr)
    #     corr_store = int(corr)
    #
    #     # If this is a mirror movement signal, store raw correction
    #
    #     if store:
    #         # Store in terms of the number of fringes for density, or vibration itself for vibration
    #         if self.fj_dcn[chan].data is None:
    #             self.fj_dcn[chan].data = np.array([corr_store])
    #             self.fj_dcn[chan].time = np.array([self.time[index]])
    #         else:
    #             self.fj_dcn[chan].data = np.append(self.fj_dcn.data, corr_store)
    #             self.fj_dcn[chan].time = np.append(self.fj_dcn.time, self.time[index])
    #
    #         kg1_signals.density[chan].correct_fj(corr_ne, time=start_time, correct_type="zeroend", corr_dcn=corr_dcn)
    #         kg1_signals.vibration[chan].correct_fj(corr_vib, time=start_time, correct_type="zeroend", corr_met=corr_met)
    #     else:
    #         logger.debug("Setting the end to zero from {}".format(start_time))
    #         # Set end to zero from ind_time (corresponds to CORRECT_TIME)
    #         kg1_signals.density[chan].correct_fj(corr_ne, index=ind_time, correct_type="zeroend", corr_dcn=corr_dcn)
    #         kg1_signals.vibration[chan].correct_fj(corr_vib, index=ind_time, correct_type="zeroend", corr_met=corr_met)
    #


    # ------------------------

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

    # # ------------------------
    # def uncorrect_fj(self, corr, index):
    #     """
    #     Uncorrect a fringe jump by corr, from the time corresponding to index onwards.
    #     Not used ATM. Will need more testing if we want to use it... Suspect isclose is wrong.
    #
    #     :param corr: Correction to add to the data
    #     :param index: Index from which to make the correction
    #
    #     """
    #     # Check we made a correction at this time.
    #     ind_corr = np.where(np.isclose(self.corrections.time, self.time[index], atol=5e-5, rtol=1e-6) == 1)
    #     if np.size(ind_corr) == 0:
    #         return
    #
    #     # Uncorrect correction
    #     self.data[index:] = self.data[index:] + corr
    #
    #     self.corrections.data = np.delete(self.corrections.data, ind_corr)
    #     self.corrections.time = np.delete(self.corrections.time, ind_corr)
    #
    # # ------------------------
    # def correct_fj(self, corr, time=None, index=None, store=True, correct_type="", corr_dcn=None, corr_met=None):
    #     """
    #     Shifts all data from time onwards, or index onwards,
    #     down by corr. Either time or index must be specified
    #
    #     :param corr: The correction to be subtracted
    #     :param time: The time from which to make the correction (if this is specified index is ignored)
    #     :param index: The index from which to make the correction
    #     :param store: To record the correction set to True
    #     :param correct_type: String describing which part of the code made the correction
    #     :param corr_dcn: Only for use with lateral channels. Stores the correction,
    #                      in terms of the number of FJ in DCN laser (as opposed to in the combined density)
    #     :param corr_met: Only for use with lateral channels. Stores the correction,
    #                      in terms of the number of FJ in the MET laser (as opposed to the correction in the vibration)
    #
    #     """
    #
    #     if time is None and index is None:
    #         logger.warning("No time or index was specified for making the FJ correction.")
    #         return
    #
    #     if time is not None:
    #         index = np.where(self.time > time),
    #         if np.size(index) == 0:
    #             logger.warning("Could not find time near {} for making the FJ correction.".format(time))
    #             return
    #
    #         index = np.min(index)
    #
    #     logger.log(5, "From index {}, time {}, subtracting {} ({} fringes)".format(index, self.time[index],
    #                                                                                    corr, corr/self.dfr))
    #     self.data[index:] = self.data[index:] - corr
    #
    #     # Store correction in terms of number of fringes
    #     corr_store = int(corr / self.dfr)
    #
    #     # If this is a mirror movement signal, store raw correction
    #     if "vib" in self.signal_type:
    #         corr_store = corr
    #
    #     if store:
    #         # Store in terms of the number of fringes for density, or vibration itself for vibration
    #         if self.corrections.data is None:
    #             self.corrections.data = np.array([corr_store])
    #             self.corrections.time = np.array([self.time[index]])
    #         else:
    #             self.corrections.data = np.append(self.corrections.data, corr_store)
    #             self.corrections.time = np.append(self.corrections.time, self.time[index])
    #
    #         self.correction_type = np.append(self.correction_type, correct_type)
    #
    #         # Also store corresponding correction for the DCN & MET lasers (for use with lateral channels only)
    #         if corr_dcn is not None:
    #             self.correction_dcn = np.append(self.correction_dcn, corr_dcn)
    #
    #         if corr_met is not None:
    #             self.correction_met = np.append(self.correction_met, corr_met)
    #
