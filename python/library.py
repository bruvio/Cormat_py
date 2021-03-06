# ----------------------------
__author__ = "B. Viola"
# ----------------------------
import logging
logger = logging.getLogger(__name__)
import sys
import os
from importlib import import_module



### procedure to load JET related python packages
### if package is not found an error message is displayed
libnames = ['ppf']
relative_imports = []


for libname in libnames:
    try:
        lib = import_module(libname)
    except:
        exc_type, exc, tb = sys.exc_info()
        print(os.path.realpath(__file__))
        print(exc)
    else:
        globals()[libname] = lib

for libname in relative_imports:
    try:
        anchor = libname.split('.')
        libr = anchor[0]
        package = anchor[1]

        lib = import_module(libr,package=package)
    except:
        exc_type, exc, tb = sys.exc_info()
        print(os.path.realpath(__file__))
        print(exc)
    else:
        globals()[libname] = lib

############
from status_flag import GetSF
import numpy as np

from numpy import arange, asscalar


import shutil
from collections import defaultdict





def test_logger():
    logger.info("info")
    logger.debug("debug")
    logger.warning("warn")
    logger.error("error")
    logger.log(5, "debug plus")


def find_duplicate_w_index(l):
    """

    :param l: list
    :return: value and indexes
    """
    values = []
    indexes = []
    dups = defaultdict(list)
    for i, e in enumerate(l):
        dups[e].append(i)

    for k, v in sorted(dups.items()):
        values.append(k)
        if len(v) >= 2:
            indexes.append(np.argmax(v))
        else:
            indexes.append(v[0])

        # if len(v) >= 2:

        # logger.log(5,'%s: %r' % (k, v))

    return values, indexes


def reconnect(signal, newhandler=None, oldhandler=None):
    """
    reconnect a signal to a new handler after disconnection from old handler
    :param signal:
    :param newhandler:
    :param oldhandler:
    :return:
    """
    while True:
        try:
            if oldhandler is not None:
                signal.disconnect(oldhandler)
            else:
                signal.disconnect()
        except TypeError:
            break
    if newhandler is not None:
        signal.connect(newhandler)


def is_empty(any_structure):
    """
    check if structure is empty
    :param any_structure:
    :return:
    """
    if any_structure:

        return False
    else:

        return True


def are_eq(a, b):
    """
    checks if a and b are equal
    :param a:
    :param b:
    :return:
    """
    return set(a) == set(b) and len(a) == len(b)


def autoscale_data(ax, data):
    ax.set_ylim(min(data), max(data))


# def find_nearest(array,value):
#     # logger.log(5, "looking for value {}".format(value))
#     idx = (np.abs(array-value)).argmin()
#
#     # logger.log(5," found at {} with index {}".format(array[idx].item(),idx))
#     return idx,array[idx].item()
def find_nearest(array, value):
    """

    :param array:
    :param value:
    :return: returns value and index of the closest element in the array to the value
    """
    import numpy as np
    import math

    array = np.sort(array)
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (
        idx == len(array)
        or math.fabs(value - array[idx - 1]) < math.fabs(value - array[idx])
    ):
        return idx - 1, array[idx - 1]
    else:
        return idx, array[idx]


def find_in_list_array(array, value):
    found = False
    array2list = np.array(array)  # numpy array
    try:
        index = list(array2list).index(value)
        found = True
        return found, index
    except ValueError:
        index = []
        return found, index


def order(lst):
    """
    checks if a list is ordered in descending or ascending way
    :param lst:
    :return:
    """
    return lst == sorted(lst) or lst == sorted(lst)[::-1]


def find_listelements_in_otherlist2(list1, list2, tstep):
    """

    :param list1:
    :param list2:
    :param tstep: minimum distance between two data points
    :return:
    """
    #
    list1 = list(list1)
    list2 = list(list2)
    # [i for e in list1 for i in list2 if e in i]
    found_list = []
    index_list = []
    for i, value in enumerate(list2):
        found, index = find_in_list_array(list1, value)
        if found:
            index_list.append(index)

    # def find_listelements_in_otherlist(list1,list2):


#     list1=list(list1)
#     list2=list(list2)
#
#     [item for item in list1 if any(x in item for x in list2)]


def find_within_range(array, minvalue, maxvalue):
    """
    returns elements of array within two values
    :param array:
    :param minvalue:
    :param maxvalue:
    :return:
    """

    # idxmin = (np.abs(array - min)).argmin()
    # idxmax = (np.abs(array - max)).argmax()

    l2 = []
    l3 = []
    if array is None:
        return l3, l2
    else:
        for i, value in enumerate(array):
            if value >= minvalue and value <= maxvalue:
                l2.append(value)
                l3.append(i)

        return l3, l2


def pyqt_set_trace():
    """Set a tracepoint in the Python debugger that works with Qt"""
    from PyQt5.QtCore import pyqtRemoveInputHook
    import pdb
    import sys

    pyqtRemoveInputHook()
    # set up the debugger
    debugger = pdb.Pdb()
    debugger.reset()
    # custom next to get outside of function scope
    debugger.do_next(None)  # run the next command
    users_frame = (
        sys._getframe().f_back
    )  # frame where the user invoked `pyqt_set_trace()`
    debugger.interaction(users_frame, None)


def norm(data):
    return (data) / (max(data) - min(data))


def normalise(signal, kg1_signal, dis_time, xlim1, xlim2):
    """

        :param signal:  second trace
        :param kg1_signal: KG1 signal
        :param dis_time: disruption time
        :return: Use ratio of maximum of signal - kg1 as the normalisation factor. Exclude region around the disruption.
        """

    if (dis_time > 0) & (dis_time > xlim2):
        (ind_dis_signal,) = np.where(
            (signal.time < dis_time) & (signal.time > xlim1) & (signal.time < xlim2)
        )
        (ind_dis,) = np.where(
            (kg1_signal.time < dis_time)
            & (kg1_signal.time > xlim1)
            & (kg1_signal.time < xlim2)
        )

    elif dis_time < 0:
        (ind_dis,) = np.where((kg1_signal.time > xlim1) & (kg1_signal.time < xlim2))
        (ind_dis_signal,) = np.where((signal.time > xlim1) & (signal.time < xlim2))

    elif (dis_time > 0) & (dis_time < xlim2) & (dis_time > xlim1):
        (ind_dis,) = np.where((kg1_signal.time < dis_time - 1))
        (ind_dis_signal,) = np.where((signal.time < dis_time - 1))

    elif (dis_time > 0) & (dis_time < xlim2) & (dis_time < xlim1):
        (ind_dis,) = np.where((kg1_signal.time < dis_time - 1))
        (ind_dis_signal,) = np.where((signal.time < dis_time - 1))

    max_kg1 = max(kg1_signal.data[ind_dis])
    max_signal = max(signal.data[ind_dis_signal])

    if max_signal == 0:
        logger.warning("divide by 0 ")
        max_signal = 1

    norm_factor = max_kg1 / max_signal

    return norm_factor


def get_seq(shot_no, dda, read_uid="JETPPF"):
    """

    :param shot_no: pulse number
    :param dda:
    :param read_uid:
    :return: get sequence of a ppf
    """
    ier = ppf.ppfgo(shot_no, seq=0)
    if ier != 0:
        return None

    ppf.ppfuid(read_uid, rw="R")

    iseq, nseq, ier = ppf.ppfdda(shot_no, dda)

    if ier != 0:
        return None

    return iseq


def get_min_max_seq(shot_no, dda="KG1V", read_uid="JETPPF"):
    """

    :param shot_no:
    :param dda:
    :param read_uid:
    :return: return min and max sequence for given pulse, dda and readuid
    min is the unvalidated sequence
    max is the last validated sequence
    """
    kg1v_seq = get_seq(shot_no, dda, read_uid)
    unval_seq = -1
    val_seq = -1
    if kg1v_seq is not None:
        unval_seq = min(kg1v_seq)
        if len(kg1v_seq) > 1:
            val_seq = max(kg1v_seq)
            return unval_seq, val_seq
        else:
            val_seq = unval_seq
            return unval_seq, val_seq


def check_SF(read_uid, pulse, seq):
    """

    :param read_uid:
    :param pulse:
    :return: list of Status Flags
    """
    logging.info("\n")
    logging.info("checking status FLAGS ")
    ier = ppf.ppfgo(pulse, seq=seq)
    ppf.ppfuid(read_uid, "r")

    ppf.ppfssr([0, 1, 2, 3, 4])

    channels = arange(0, 8) + 1
    SF_list = []

    pulse = int(pulse)

    for channel in channels:
        ch_text = "lid" + str(channel)

        if read_uid =='chain1':
            dda = 'kg1r'
        else:
            dda= 'kg1v'
        st_ch = GetSF(pulse, dda, ch_text)
        st_ch = asscalar(st_ch)
        SF_list.append(st_ch)
    logging.info("%s has the following SF %s", str(pulse), SF_list)

    return SF_list


def extract_history(filename, outputfile):
    """
    running this script will create a csv file containing a list of all the
    ppf that have been created with Cormat_py code

    the script reads a log file (generally in /u/user/work/Python/Cormat_py)


    and writes an output file in the current working directory

    the file is formatted in this way
    shot: {} user: {} date: {} seq: {} by: {}
    user is the write user id
    by is the userid of the user of the code
    the output is appended and there is a check on duplicates

    if the user have never run KG1_py code the file will be empty

    :param filename: name of KG1L (or KG1H) diary to be read
    :param outputfile: name of the output file
    :return:

    """
    import os

    if os.path.exists(filename):

        with open(filename, "r") as f_in:
            lines = f_in.readlines()
            for index, line in enumerate(lines):
                if "shot" in str(line):

                    dummy = lines[index].split()
                    shot = int(dummy[1])
                    logger.log(5, "shot {}".format(shot))
                    user = str(dummy[3])
                    date = str(dummy[5])

                    # #             dummy = lines[index + 1].split()
                    sequence = dummy[7]

                    writtenby = dummy[10]
                    # #
                    #             month =(dummy[6])
                    #             day =(dummy[7])
                    #             year =(dummy[9])
                    #             logging.info(month,day,year)
                    #             date = datetime.date(int(year),strptime(month,'%b').tm_mon , int(day))

                    # logging.info(shot, user, date, sequence,writtenby)
                    # return
                    string_to_write = "shot: {} user: {} date: {} seq: {} by: {}\n".format(
                        str(shot).strip(),
                        user.strip(),
                        str(date).strip(),
                        str(sequence).strip(),
                        writtenby.strip(),
                    )

                    if os.path.exists(outputfile):
                        if check_string_in_file(outputfile, string_to_write):
                            pass
                        else:
                            with open(outputfile, "a+") as f_out:
                                f_out.write(string_to_write)
                            f_out.close()
                    else:
                        with open(outputfile, "a+") as f_out:
                            f_out.write(string_to_write)
                        f_out.close()

        f_in.close()
    else:
        f_in = open(filename, "w")
        f_in.close()
        string_to_write = "shot: {} user: {} date: {} seq: {} by: {}\n".format(
            str(00000), "unknown", str("00-00-00"), str(000), "unknown"
        )
        if os.path.exists(outputfile):
            if check_string_in_file(outputfile, string_to_write):
                pass
            else:
                with open(outputfile, "a+") as f_out:
                    f_out.write(string_to_write)
                f_out.close()
        else:
            with open(outputfile, "a+") as f_out:
                f_out.write(string_to_write)
            f_out.close()


def check_string_in_file(filename, string):
    """

    :param filename:
    :param string:
    :return: checks if the string is in that file
    """
    with open(filename) as myfile:
        if string in myfile.read():
            return True
        else:
            return False


def equalsFile(firstFile, secondFile, blocksize=65536):
    """

    :param firstFile:
    :param secondFile:
    :param blocksize:
    :return: returns True if files are the same,i.e. secondFile has same checksum as first
    """

    if os.path.getsize(firstFile) != os.path.getsize(secondFile):
        return False
    else:
        firstFile = open(firstFile, "rb")
        secondFile = open(secondFile, "rb")
        buf1 = firstFile.read(blocksize)
        buf2 = secondFile.read(blocksize)
    while len(buf1) > 0:
        if buf1 != buf2:
            return False
        buf1, buf2 = firstFile.read(blocksize), secondFile.read(blocksize)
    return True





#
# =============================================================================
def copy_changed_kg1_to_save(src, dst, filename):
    """

    :param src:
    :param dst:
    :param filename:
    :return: copies file from src folder to dst
    """

    src = "./" + src + "/" + filename
    dst = "./" + dst + "/" + filename

    copyfile(src, dst)


# -----------------------


# def delete_files_in_folder(folder):
#     try:
#         for root, dirs, files in os.walk(folder):
#             for f in files:
#                 os.unlink(os.path.join(root, f))
#                 # for d in dirs:
#                 #     shutil.rmtree(os.path.join(root, d))
#         return True
#     except:
#         return False

def delete_files_in_folder(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile("./"+path+"/kg1_data.pkl"):
        os.remove(path+os.sep+'kg1_data.pkl')  # remove the file
    if os.path.isfile("./"+path+"/data.pkl"):
        os.remove(path+os.sep+'data.pkl')  # remove the file
    for channel in range(1,13):
        if os.path.isfile("./"+path+"/vib_chan"
                            + str(channel)
                            + ".pkl"):
            os.remove(path+os.sep+'vib_chan'
                            + str(channel)
                            + ".pkl") # remove the file
        if os.path.isfile("./"+path+"/den_chan"
                            + str(channel)
                            + ".pkl"):
            os.remove(path+os.sep+'den_chan'
                            + str(channel)
                            + ".pkl") # remove the file
        if os.path.isfile("./"+path+"/fj_dcn_chan"
                            + str(channel)
                            + ".pkl"):
            os.remove(path+os.sep+'fj_dcn_chan'
                            + str(channel)
                            + ".pkl")  # remove the file
        if os.path.isfile("./"+path+"/fj_met_chan"
                            + str(channel)
                            + ".pkl"):
            os.remove(path+os.sep+'fj_met_chan'
                            + str(channel)
                            + ".pkl")  # remove the file







# Declare and register callbacks
def on_xlims_change(ax):

    print("updated xlims: ", ax.get_xlim())
    return ax.get_xlim()


def on_ylims_change(ax):
    print("updated ylims: ", ax.get_ylim())
    return ax.get_ylim()
