
# ----------------------------
__author__ = "B. Viola"
# ----------------------------
from status_flag import GetSF
import numpy as np
from ppf import *
import logging
from numpy import arange,asscalar

def norm(data):
    return (data)/(max(data)-min(data))

def normalise(signal, kg1_signal, dis_time):
        # ----------------------
        # Use ratio of maximum of signal - kg1 as the normalisation factor.
        # Exclude region around the disruption.
        # ----------------------
        if dis_time > 0:
                ind_dis, = np.where((kg1_signal.time < dis_time - 1))

                max_kg1 = max(kg1_signal.data[ind_dis])
        else:
                max_kg1 = max(kg1_signal.data)

        max_signal = max(signal.data)

        #    print("max kg1 {} max signal {}".format(max_kg1, max_signal))

        norm_factor = max_kg1 / max_signal
        signal.data = signal.data * norm_factor

        return signal.data

def get_seq(shot_no, dda, read_uid="JETPPF"):
    ier = ppfgo(shot_no, seq=0)
    if ier != 0:
        return None

    ppfuid(read_uid, rw="R")

    iseq, nseq, ier = ppfdda(shot_no, dda)

    if ier != 0:
        return None

    return iseq

def get_min_max_seq(shot_no, dda="KG1V", read_uid="JETPPF"):
    kg1v_seq = get_seq(shot_no, dda,read_uid)
    unval_seq = -1
    val_seq = -1
    if kg1v_seq is not None:
        unval_seq = min(kg1v_seq)
        if len(kg1v_seq) > 1:
            val_seq = max(kg1v_seq)

    return unval_seq, val_seq

def check_SF(read_uid,pulse):
        logging.info('\n')
        logging.info('checking status FLAGS ')

        ppfuid(read_uid, "r")

        ppfssr(i=[0, 1, 2, 3, 4])

        channels = arange(0, 8) + 1
        SF_list = []

        pulse = int(pulse)

        for channel in channels:
                ch_text = 'lid' + str(channel)

                st_ch = GetSF(pulse, 'kg1v', ch_text)
                st_ch = asscalar(st_ch)
                SF_list.append(st_ch)
        logging.info('%s has the following SF %s', str(pulse), SF_list)

        return SF_list
