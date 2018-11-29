"""
Class to read and store KG1 PPF data for one channel.
Reads in LIDX, FCX, MIRX, JXBX, TYPX

Needs modifying so it would work with old KG1V & new KG1V dtypes
"""

import logging

import numpy as np
from ppf_write import write_ppf

from signal_base import SignalBase

logger = logging.getLogger(__name__)

# ----------------------------
__author__ = "L. Kogan"
# ----------------------------


class Kg1PPFData:

    # ------------------------
    def __init__(self, constants):
        """
        Init function

        :param constants: instance of Kg1Consts class
        """
        self.constants = constants

        self.dda = "KG1R"
        self.density = None
        self.vibration = None
        self.fj_dcn = None
        self.fj_met = None
        self.jxb = None
        self.bp_dcn = None
        self.bp_met = None
        self.status = 0
        self.type = ""
        self.mode = ""

    # ------------------------
    def read_data(self, shot_no, chan, read_uid="JETPPF", all_status=False):
        """
        Read in PPF data for KG1V for a given channel

        :param shot_no: shot number
        :param chan: channel
        :param read_uid: read UID
        :param all_status: if True, then read in even if status flag is 4
        :return: True if data was read in successfully, False otherwise
        """
        if chan in self.constants.kg1r_ppf_ne.keys():
            nodename = self.constants.kg1r_ppf_ne[chan]
            density = SignalBase(self.constants)
            dda = nodename[:nodename.find('/')]
            dtype = nodename[nodename.find('/')+1:]
            status = density.read_data_ppf(dda, dtype, shot_no, read_bad=True, read_uid=read_uid)

            # We are only interested in keeping the data if it has already been validated
            if density.data is not None and (0 < status < 4) and not all_status:
                logger.log(5, "PPF data chan {}".format(status))
                self.density = density
                self.status = status
            else:
                return False
        else:
            return False

        if chan in self.constants.kg1r_ppf_vib.keys():
            nodename = self.constants.kg1r_ppf_vib[chan]
            vibration = SignalBase(self.constants)
            dda = nodename[:nodename.find('/')]
            dtype = nodename[nodename.find('/')+1:]
            status = vibration.read_data_ppf(dda, dtype, shot_no, read_bad=True, read_uid=read_uid)

            if vibration.data is not None:
                self.vibration = vibration

        if chan in self.constants.kg1r_ppf_fj_dcn.keys():
            nodename = self.constants.kg1r_ppf_fj_dcn[chan]
            fj = SignalBase(self.constants)

            dda = nodename[:nodename.find('/')]
            dtype = nodename[nodename.find('/')+1:]
            status = fj.read_data_ppf(dda, dtype, shot_no, read_bad=True, read_uid=read_uid)

            if fj.data is not None:
                self.fj_dcn = fj

        if chan in self.constants.kg1r_ppf_fj_met.keys():
            nodename = self.constants.kg1r_ppf_fj_met[chan]
            fj = SignalBase(self.constants)

            dda = nodename[:nodename.find('/')]
            dtype = nodename[nodename.find('/')+1:]
            status = fj.read_data_ppf(dda, dtype, shot_no, read_bad=True, read_uid=read_uid)

            if fj.data is not None:
                self.fj_met = fj

        if chan in self.constants.kg1r_ppf_bp_dcn.keys():
            nodename = self.constants.kg1r_ppf_bp_dcn[chan]
            bp = SignalBase(self.constants)

            dda = nodename[:nodename.find('/')]
            dtype = nodename[nodename.find('/')+1:]
            status = bp.read_data_ppf(dda, dtype, shot_no, read_bad=True, read_uid=read_uid)

            if bp.data is not None:
                self.bp_dcn = bp

        if chan in self.constants.kg1r_ppf_bp_met.keys():
            nodename = self.constants.kg1r_ppf_bp_met[chan]
            bp = SignalBase(self.constants)

            dda = nodename[:nodename.find('/')]
            dtype = nodename[nodename.find('/')+1:]
            status = bp.read_data_ppf(dda, dtype, shot_no, read_bad=True, read_uid=read_uid)

            if bp.data is not None:
                self.bp_met = bp

        if chan in self.constants.kg1r_ppf_jxb.keys():
            nodename = self.constants.kg1r_ppf_jxb[chan]
            jxb = SignalBase(self.constants)
            dda = nodename[:nodename.find('/')]
            dtype = nodename[nodename.find('/')+1:]
            status = jxb.read_data_ppf(dda, dtype, shot_no, read_bad=True, read_uid=read_uid)

            if jxb.data is not None:
                self.jxb = jxb

        if chan in self.constants.kg1r_ppf_type.keys():
            nodename = self.constants.kg1r_ppf_type[chan]
            sig_type = SignalBase(self.constants)
            dda = nodename[:nodename.find('/')]
            dtype = nodename[nodename.find('/')+1:]
            status = sig_type.read_data_ppf(dda, dtype, shot_no, read_bad=True, read_uid=read_uid)

            if sig_type.data is not None:
                ind_type = sig_type.ihdata.find("SIG TYPE:")+len("SIG TYPE:")+1
                ind_chan = sig_type.ihdata.find("CH.")-1
                self.type = sig_type.ihdata[ind_type:ind_chan]

        return True

    # ------------------------
    def write_data(self, chan, shot_no, itref):
        """
        Write data to PPF system

        :param chan: channel
        :param shot_no: shot number
        :param itref: itref to use for the timebase
        :return: write error, itref
        """

        # LID
        dtype_lid = "LID{}".format(chan)
        comment = "DATA FROM KG1V CHANNEL {}".format(chan)

        logger.debug("Writing PPF LID {}".format(chan))

        write_err, itref = write_ppf(shot_no, self.dda, dtype_lid, self.density.data,
                                     time=self.density.time, comment=comment,
                                     unitd='M-2', unitt='SEC', itref=itref,
                                     nt=len(self.density.time), status=self.status)

        if write_err != 0:
            logger.error("Failed to write {}/{}. Errorcode {}".format(self.dda, dtype_lid, write_err))
            return write_err, itref

        # DCN fringes
        if self.fj_dcn is not None:
            dtype_fc = "FCD{}".format(chan)
            comment = "DCN FRINGE CORRECTIONS CH.{}".format(chan)
            write_err, itref_written = write_ppf(shot_no, self.dda, dtype_fc, self.fj_dcn.data,
                                                 time=self.fj_dcn.time, comment=comment,
                                                 unitd=" ", unitt="SEC", itref=-1,
                                                 nt=len(self.fj_dcn.time), status=None)

            if write_err != 0:
                return write_err, itref

        # DCN laser points with bad amplitude
        if self.bp_dcn is not None:
            dtype_bp = "BPD{}".format(chan)
            comment = "DCN LASER BAD POINTS CH.{}".format(chan)
            write_err, itref_written = write_ppf(shot_no, self.dda, dtype_bp, self.bp_dcn.data,
                                                 time=self.bp_dcn.time, comment=comment,
                                                 unitd=" ", unitt="SEC", itref=-1,
                                                 nt=len(self.bp_dcn.time), status=None)

            if write_err != 0:
                return write_err, itref

        if self.vibration is not None:
            # Vibration
            dtype_vib = "MIR{}".format(chan)
            comment = "MOVEMENT OF MIRROR {}".format(chan)
            write_err, itref_written = write_ppf(shot_no, self.dda, dtype_vib, self.vibration.data,
                                                 time=self.vibration.time, comment=comment,
                                                 unitd='M', unitt='SEC', itref=itref,
                                                 nt=len(self.vibration.time), status=self.status)
            if write_err != 0:
                logger.error("Failed to write {}/{}. Errorcode {}".format(self.dda, dtype_vib, write_err))
                return write_err, itref

            # JXB movement
            dtype_jxb = "JXB{}".format(chan)
            comment = "JxB CALC. MOVEMENT CH.{}".format(chan)
            write_err, itref_written = write_ppf(shot_no, self.dda, dtype_jxb, self.jxb.data,
                                                 time=self.jxb.time, comment=comment,
                                                 unitd='M', unitt='SEC', itref=itref,
                                                 nt=len(self.jxb.time), status=self.status)

            if write_err != 0:
                return write_err, itref

            # MET fringes
            if self.fj_met is not None:
                dtype_fc = "FCM{} ".format(chan)
                comment = "MET FRINGE CORRECTIONS CH.{}".format(chan)
                write_err, itref_written = write_ppf(shot_no, self.dda, dtype_fc, self.fj_met.data,
                                                     time=self.fj_met.time, comment=comment,
                                                     unitd=" ", unitt="SEC", itref=-1,
                                                     nt=len(self.fj_met.time), status=None)

                if write_err != 0:
                    return write_err, itref

            # MET laser points with bad amplitude
            if self.bp_met is not None:
                dtype_bp = "BPM{}".format(chan)
                comment = "MET LASER BAD POINTS CH.{}".format(chan)
                write_err, itref_written = write_ppf(shot_no, self.dda, dtype_bp, self.bp_met.data,
                                                     time=self.bp_met.time, comment=comment,
                                                     unitd=" ", unitt="SEC", itref=-1,
                                                     nt=len(self.bp_met.time), status=None)

                if write_err != 0:
                    return write_err, itref

        # Write signal type
        dtype_type = "TYP{}".format(chan)
        comment = "SIG TYPE: "+self.type+" CH.{}".format(chan)
        write_err, itref_written = write_ppf(shot_no, self.dda, dtype_type, np.array([1]),
                                            time=np.array([0]), comment=comment,
                                            unitd=" ", unitt=" ", itref=-1,
                                            nt=1, status=None)

        return write_err, itref
