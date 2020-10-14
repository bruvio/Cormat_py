#!/usr/bin/env python
"""
Class that runs CORMAT_py GUI
"""


# ----------------------------
__author__ = "Bruno Viola"
__Name__ = "CORMAT_py"
__version__ = "2.3"
__release__ = "2"
__maintainer__ = "Bruno Viola"
__email__ = "bruno.viola@ukaea.uk"
# __status__ = "Testing"
__status__ = "Production"


import warnings

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=DeprecationWarning)

import logging

logger = logging.getLogger(__name__)
import sys
import os
from importlib import import_module
from save_2_dropbox import *
from numpy import arange

libnames = ["ppf"]
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
        anchor = libname.split(".")
        libr = anchor[0]
        package = anchor[1]

        lib = import_module(libr)
        # lib = import_module(libr,package=package)
    except:
        exc_type, exc, tb = sys.exc_info()
        print(os.path.realpath(__file__))
        print(exc)
    else:
        globals()[libr] = lib


import matplotlib

matplotlib.use("QT4Agg")
import argparse
from types import SimpleNamespace
from logging.handlers import RotatingFileHandler
from logging import handlers
import os
import pathlib

# from pickle import dump,load
import pickle
import platform
import datetime
import time
from pathlib import Path
import CORMAT_GUI
import pdb
import matplotlib.pyplot as plt

# from PyQt4 import QtCore, QtGui
#
# from PyQt4.QtCore import *
# from PyQt4.QtGui import *
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from areyousure_gui import Ui_areyousure_window
from accept_suggestion import Ui_suggestion_window
from consts import Consts
from elms_data import ElmsData
from find_disruption import find_disruption
from hrts_data import HRTSData
from kg1_ppf_data import Kg1PPFData
from kg4_data import Kg4Data
from library import *  # containing useful function
from lidar_data import LIDARData
from mag_data import MagData
from matplotlib import gridspec
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import AutoMinorLocator
from signal_kg1 import SignalKg1
from signal_base import SignalBase
from nbi_data import NBIData
from pellet_data import PelletData
from ppf_write import *
from signal_base import SignalBase
from custom_formatters import MyFormatter, QPlainTextEditLogger, HTMLFormatter
from support_classes import LineEdit, Key, KeyBoard, MyLocator
import inspect
import fileinput
import cProfile, pstats, io
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
import inspect
import getpass


qm = QMessageBox
qm_permanent = QMessageBox
plt.rcParams["savefig.directory"] = os.chdir(os.getcwd())
my= lambda: inspect.stack()[1][3]
data = SimpleNamespace()
data.constants = Consts("consts.ini", __version__)

# backup for kg1 data
data.kg1_original = {}
# -------------------------------
# store normalised kg1?
data.kg1_norm = {}
# ----------------------
# initialise data
data.KG1_data = {}
data.KG4_data = {}
data.MAG_data = {}
data.PELLETS_data = {}
data.ELM_data = {}
data.HRTS_data = {}
data.NBI_data = {}
data.is_dis = {}
data.dis_time = {}
data.LIDAR_data = {}

# list where storing data point selected by user clicking on canvas
data.coord_ch1 = []
data.coord_ch2 = []
data.coord_ch3 = []
data.coord_ch4 = []
data.coord_ch5 = []
data.coord_ch6 = []
data.coord_ch7 = []
data.coord_ch8 = []

interp_kg1v = False

####
totalcorrections_den = np.empty([7])
totalcorrections_vib = np.empty([7])

# storing backup of data when zeroing
data.zeroingbackup_den = [[], [], [], [], [], [], [], []]
data.zeroingbackup_vib = [[], [], [], [], [], [], [], []]

#
data.zeroed = np.zeros(
    8, dtype=bool
)  # array that stores info is channel has been tail zeroed
data.zeroing_start = np.full(8, 1e6, dtype=int)
data.zeroing_stop = np.full(8, 0, dtype=int)

data.data_changed = np.zeros(
    8, dtype=bool
)  # array that stores info if channel data have been changed
data.statusflag_changed = np.zeros(
    8, dtype=bool
)  # array that stores info is channel status flag have been changed
#

#

# -------------------------------
# old pulse contains information on the last pulse analysed
data.old_pulse = None
# pulse is the current pulse
data.pulse = None
# -------------------------------
# initialisation of control variables
# -------------------------------
# set saved status to False

data.saved = False


def readdata(pulse, read_uid):

    """
        function that reads data as described in const.ini
        :return: True if success
                False if error
                saves data to pickle files: one just for KG1 (kg1_data) and one for everything else (data.pkl)
        """

    # -------------------------------
    # 1. Read in Magnetics data
    # -------------------------------
    data.pulse = pulse
    data.sequence = 0
    data.read_uid = read_uid
    logger.info("             Reading in magnetics data.\n")
    data.MAG_data = MagData(data.constants)
    success = data.MAG_data.read_data(data.pulse)
    if not success:
        logging.error(
            "no MAG data for pulse {} with uid {}\n".format(data.pulse, read_uid)
        )

    # -------------------------------
    # 2. Read in KG1 data
    # -------------------------------
    logger.info("             Reading in KG1 data.\n")
    data.KG1_data = Kg1PPFData(data.constants, data.pulse, data.sequence)

    read_uid = read_uid
    success = data.KG1_data.read_data(data.pulse, read_uid=read_uid)
    logger.log(5, "success reading KG1 data?".format(success))
    # Exit if there were no good signals
    # If success == 1 it means that at least one channel was not available. But this shouldn't stop the rest of the code
    # from running.
    if not success:
        # success = 11: Validated PPF data is already available for all channels
        # success = 8: No good JPF data was found
        # success = 9: JPF data was bad
        logging.error(
            "no KG1V data for pulse {} with uid {}\n".format(data.pulse, read_uid)
        )
        return False
        # -------------------------------
    # -------------------------------
    # 4. Read in KG4 data
    # -------------------------------
    logger.info("             Reading in KG4 data.\n")
    data.KG4_data = Kg4Data(data.constants)
    data.KG4_data.read_data(data.MAG_data, data.pulse)

    # -------------------------------
    # 5. Read in pellet signals
    # -------------------------------
    logger.info("             Reading in pellet data.\n")
    data.PELLETS_data = PelletData(data.constants)
    data.PELLETS_data.read_data(data.pulse)

    # -------------------------------
    # 6. Read in NBI data.
    # -------------------------------
    logger.info("             Reading in NBI data.\n")
    data.NBI_data = NBIData(data.constants)
    data.NBI_data.read_data(data.pulse)

    # -------------------------------
    # 7. Check for a disruption, and set status flag near the disruption to 4
    #    If there was no disruption then dis_time elements are set to -1.
    #    dis_time is a 2 element list, being the window around the disruption.
    #    Within this time window the code will not make corrections.
    # -------------------------------
    logger.info("             Find disruption.\n")
    is_dis, dis_window, dis_time = find_disruption(
        data.pulse, data.constants, data.KG1_data
    )
    data.is_dis = is_dis
    data.dis_time = dis_time
    logger.info("Time of disruption {}\n".format(dis_time))

    # -------------------------------
    # 8. Read in Be-II signals, and find ELMs
    # -------------------------------
    logger.info("             Reading in ELMs data.\n")
    data.ELM_data = ElmsData(data.constants, data.pulse, dis_time=dis_time)

    # -------------------------------
    # 9. Read HRTS data
    # # -------------------------------
    logger.info("             Reading in HRTS data.\n")
    data.HRTS_data = HRTSData(data.constants)
    data.HRTS_data.read_data(data.pulse)

    # # # # -------------------------------
    # # # 10. Read LIDAR data
    # # # -------------------------------
    logger.info("             Reading in LIDAR data.\n")
    data.LIDAR_data = LIDARData(data.constants)
    data.LIDAR_data.read_data(data.pulse)

    # read status flag

    data.SF_list = check_SF(read_uid, data.pulse, data.sequence)

    [
        data.SF_ch1,
        data.SF_ch2,
        data.SF_ch3,
        data.SF_ch4,
        data.SF_ch5,
        data.SF_ch6,
        data.SF_ch7,
        data.SF_ch8,
    ] = data.SF_list

    data.SF_old1 = data.SF_ch1
    data.SF_old2 = data.SF_ch2
    data.SF_old3 = data.SF_ch3
    data.SF_old4 = data.SF_ch4
    data.SF_old5 = data.SF_ch5
    data.SF_old6 = data.SF_ch6
    data.SF_old7 = data.SF_ch7
    data.SF_old8 = data.SF_ch8

    try:
        data.unval_seq, data.val_seq = get_min_max_seq(
            data.pulse, dda="KG1V", read_uid=read_uid
        )
    except TypeError:
        logger.error("impossible to read sequence for user {}".format(read_uid))
        return

    if read_uid.lower() == "jetppf":
        logger.info(
            "{} last public seq is {}\n".format(str(data.pulse), str(data.val_seq))
        )
        if "Automatic Corrections" in data.KG1_data.mode:
            pass
        else:
            try:
                data.KG1_data.correctedby = data.KG1_data.mode.split(" ")[2]
                logger.info(
                    "{} corrected by {}\n \n".format(
                        str(data.pulse), data.KG1_data.correctedby
                    )
                )
            except IndexError:
                logger.error("error!")

    else:
        if "Automatic Corrections" in data.KG1_data.mode:
            data.KG1_data.correctedby = data.KG1_data.mode
            logger.info(
                "{} last private seq is {} by {}\n".format(
                    str(data.pulse), str(data.val_seq), data.KG1_data.correctedby,
                )
            )
            logger.info("userid is {}".format(read_uid))

        else:
            try:
                data.KG1_data.correctedby = data.KG1_data.mode.split(" ")[2]
                logger.info(
                    "{} last seq is {} by {}\n".format(
                        str(data.pulse), str(data.val_seq), data.KG1_data.correctedby,
                    )
                )
            except IndexError:
                logger.error("error!")

    logger.info("\n \n  pulse has disrupted? {}\n \n".format(data.is_dis))

    data.KG1_data_public = Kg1PPFData(data.constants, data.pulse, 0)

    read_uid = read_uid
    logging.info("\n reading public KG1V ppf")
    success = data.KG1_data_public.read_data(data.pulse, read_uid="jetppf")
    logger.log(5, "success reading KG1 data?".format(success))

    # read status flag from public ppf

    data.SF_list_public = check_SF("jetppf", data.pulse, 0)
    data.validated_public_channels = [
        i + 1 for i, e in enumerate(data.SF_list_public) if e != 0
    ]

    # if any(data.SF_list_public) in [1, 2, 3]:
    if bool(set(data.SF_list_public) & set([1, 2, 3])):
        # if set(data.SF_list_public).intersection(set([1, 2, 3])) is True:
        logger.warning(
            "\n \n there is already a saved public PPF with validated channels! \n \n "
        )

    # logger.info('unval_seq {}, val_seq {}'.format(str(data.unval_seq),str(data.val_seq)))
    # save data to pickle into saved folder
    save_to_pickle("saved")
    # save data to pickle into scratch folder
    save_to_pickle("scratch")
    # save KG1 data on different file (needed later when applying corrections)
    save_kg1("saved")
    save_kg1("scratch")
    data.saved = False
    data.data_changed = np.full(8, False, dtype=bool)
    data.statusflag_changed = np.full(8, False, dtype=bool)
    # dump KG1 data on different file (used to autosave later when applying corrections)
    dump_kg1

    # if "Automatic Corrections" in data.KG1_data.mode:
    #     data.KG1_data.correctedby = data.KG1_data.mode
    #     logger.info('{} last seq is {} by {}'.format(str(data.pulse),
    #                                                  str(data.val_seq),
    #                                                  data.KG1_data.correctedby))
    # else:
    #     data.KG1_data.correctedby = \
    #         data.KG1_data.mode.split(" ")[2]
    #     logger.info('{} last validated seq is {} by {}'.format(
    #         str(data.pulse),
    #         str(data.val_seq), data.KG1_data.correctedby))

    # backup of channel data to single files
    # density
    for chan in data.KG1_data.density.keys():
        vars()["den_chan" + str(chan)] = data.KG1_data.density[chan]

        with open("./saved/den_chan" + str(chan) + ".pkl", "wb") as f:
            pickle.dump([vars()["den_chan" + str(chan)]], f)
        f.close()
    #     fj_fcn
    for chan in data.KG1_data.fj_dcn.keys():
        vars()["fj_dcn_chan" + str(chan)] = data.KG1_data.fj_dcn[chan]

        with open("./saved/fj_dcn_chan" + str(chan) + ".pkl", "wb") as f:
            pickle.dump([vars()["fj_dcn_chan" + str(chan)]], f)
        f.close()
    #     fj_met
    for chan in data.KG1_data.fj_met.keys():
        vars()["fj_met_chan" + str(chan)] = data.KG1_data.fj_met[chan]

        with open("./saved/fj_met_chan" + str(chan) + ".pkl", "wb") as f:
            pickle.dump([vars()["fj_met_chan" + str(chan)]], f)
        f.close()

    #     vibration
    for chan in sorted(data.KG1_data.vibration.keys()):
        vars()["vib_chan" + str(chan)] = data.KG1_data.vibration[chan]
        with open("./saved/vib_chan" + str(chan) + ".pkl", "wb") as f:
            pickle.dump([vars()["vib_chan" + str(chan)]], f)

        f.close()

    return True


# ------------------------
def save_to_pickle( folder):
    """
    saves to pickle experimental data
    :param folder: for now user can save either to saved or scratch folder
    :return:
    """
    logger.info(" saving pulse data to {}\n".format(folder))

    with open("./" + folder + "/data.pkl", "wb") as f:
            pickle.dump(
                [
                    data.pulse,
                    data.sequence,
                    data.KG1_data,
                    data.KG4_data,
                    data.MAG_data,
                    data.PELLETS_data,
                    data.ELM_data,
                    data.HRTS_data,
                    data.NBI_data,
                    data.is_dis,
                    data.dis_time,
                    data.LIDAR_data,
                    data.zeroing_start,
                    data.zeroing_stop,
                    data.zeroed,
                    data.zeroingbackup_den,
                    data.zeroingbackup_vib,
                    data.data_changed,
                    data.statusflag_changed,
                    data.validated_public_channels,
                    data.SF_list_public,
                ],
                f,
            )
    f.close()
    logger.info(" data saved to {}\n".format(folder))
    if folder == 'saved':
        pathlib.Path("./" + folder + os.sep+ str(data.pulse)).mkdir(parents=True,
                                                     exist_ok=True)
        with open("./" + folder + os.sep+ str(data.pulse)+"/data.pkl", "wb") as f:
            pickle.dump(
                [
                    data.pulse,
                    data.sequence,
                    data.KG1_data,
                    data.KG4_data,
                    data.MAG_data,
                    data.PELLETS_data,
                    data.ELM_data,
                    data.HRTS_data,
                    data.NBI_data,
                    data.is_dis,
                    data.dis_time,
                    data.LIDAR_data,
                    data.zeroing_start,
                    data.zeroing_stop,
                    data.zeroed,
                    data.zeroingbackup_den,
                    data.zeroingbackup_vib,
                    data.data_changed,
                    data.statusflag_changed,
                    data.validated_public_channels,
                    data.SF_list_public,
                ],
                f,
            )
        f.close()


# ------------------------
def save_kg1( folder):
    """
    module that saves just kg1 data to folder
    :param folder:
    :return:
    """

    logger.debug(" saving KG1 data to {}".format(folder))
    try:
        with open("./" + folder + "/kg1_data.pkl", "wb") as f:
            pickle.dump(
                [
                    data.KG1_data,
                    data.SF_list,
                    data.unval_seq,
                    data.val_seq,
                    data.read_uid,
                    data.zeroing_start,
                    data.zeroing_stop,
                    data.zeroingbackup_den,
                    data.zeroingbackup_vib,
                    data.data_changed,
                    data.statusflag_changed,
                    data.validated_public_channels,
                    data.SF_list_public,
                ],
                f,
            )
        f.close()
        logger.info(" KG1 data saved to {}\n".format(folder))
    except AttributeError:
        logger.error("failed to save, check data!")

    logger.debug(" saving KG1 data to {}".format(folder))
    try:
        if folder == 'saved':
            pathlib.Path(
                "./" + folder + os.sep + str(data.pulse)).mkdir(
                parents=True,
                exist_ok=True)
            with open("./" + folder + os.sep+str(data.pulse)+ "/kg1_data.pkl", "wb") as f:
                pickle.dump(
                    [
                        data.KG1_data,
                        data.SF_list,
                        data.unval_seq,
                        data.val_seq,
                        data.read_uid,
                        data.zeroing_start,
                        data.zeroing_stop,
                        data.zeroingbackup_den,
                        data.zeroingbackup_vib,
                        data.data_changed,
                        data.statusflag_changed,
                        data.validated_public_channels,
                        data.SF_list_public,
                    ],
                    f,
                )
            f.close()
            logger.info(" KG1 data saved to {}\n".format(folder))
    except AttributeError:
        logger.error("failed to save, check data!")

    if folder == 'saved':
        pathlib.Path(
            "./" + folder + os.sep + str(data.pulse) ).mkdir(
            parents=True,
            exist_ok=True)

        try:
            with open("./" + folder + os.sep + str(data.pulse) + "/kg1_data.pkl", "wb") as f:
                pickle.dump(
                    [
                        data.KG1_data,
                        data.SF_list,
                        data.unval_seq,
                        data.val_seq,
                        data.read_uid,
                        data.zeroing_start,
                        data.zeroing_stop,
                        data.zeroingbackup_den,
                        data.zeroingbackup_vib,
                        data.data_changed,
                        data.statusflag_changed,
                        data.validated_public_channels,
                        data.SF_list_public,
                    ],
                    f,
                )
            f.close()
            logger.info(" KG1 data saved to {}\n".format(folder))
        except AttributeError:
            logger.error("failed to save, check data!")

# ---------------------------------
@QtCore.pyqtSlot()
def dump_kg1():
    """
    temporary save kg1 data to scratch folder
    :return:
    """
    # logger.info(' dumping KG1 data')
    checkStatuFlags()
    actual_chan = chan
    for chan in data.KG1_data.density.keys():
        chan = chan
        logging.getLogger().disabled = True
        handle_makepermbutton()
    chan = actual_chan
    logging.getLogger().disabled = False
    save_kg1("scratch")

    # logger.info(' KG1 data dumped to scratch')
    # if workspace is saved then delete data point collected (so no need to undo)
    setcoord(reset=True, chan="all")

    pathlib.Path("./saved" + os.sep+ str(data.pulse)).mkdir(parents=True,
                                                 exist_ok=True)
    with open("./saved" + os.sep+ str(data.pulse)+"/data.pkl", "wb") as f:
        pickle.dump(
            [
                data.pulse,
                data.sequence,
                data.KG1_data,
                data.KG4_data,
                data.MAG_data,
                data.PELLETS_data,
                data.ELM_data,
                data.HRTS_data,
                data.NBI_data,
                data.is_dis,
                data.dis_time,
                data.LIDAR_data,
                data.zeroing_start,
                data.zeroing_stop,
                data.zeroed,
                data.zeroingbackup_den,
                data.zeroingbackup_vib,
                data.data_changed,
                data.statusflag_changed,
                data.validated_public_channels,
                data.SF_list_public,
            ],
            f,
        )
    f.close()


# ----------------------------



if __name__ == "__main__":
    debug_map = {
        0: logging.INFO,
        1: logging.WARNING,
        2: logging.DEBUG,
        3: logging.ERROR,
        4: 5,
    }
    # this plots logger twice (black plus coloured)
    logging.addLevelName(5, "DEBUG_PLUS")
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=debug_map[0])
    # pulselist = [97094,
    # 97095,
    # 97096,
    # 97035,
    # 97037,
    # 97038,
    # 97120,
    # 97121,
    # 97122,
    # 97123,
    # 97124,
    # 97125,
    # 97126,
    # 97128,
    # 97129,
    # 97130,
    # 97131,
    # 97133,
    # 97134]
    # pulselist = [
    #     96931,
    #     96536,
    #     96924,
    #     96925,
    #     96926,
    #     96927,
    #     96928,
    #     96289,
    #     96290,
    #     96291,
    #     96292,
    #     96293,
    #     96294,
    #     96295,
    #     96424,
    #     96296,
    #     96298,
    #     96297,
    #     96940,
    #     96301,
    #     96942,
    #     96943,
    #     96724,
    #     96729,
    #     96730,
    #     96731,
    #     96994,
    #     96482,
    #     96996,
    #     96998,
    #     96745,
    #     96749,
    #     97134,
    #     97133,
    #     96499,
    #     96929,
    #     96892,
    #     96893,
    # ]
    # pulselist = [97133,97134]
    pulselist = [97514,
97515,
97516,
97517,
97518,
97521,
97522,
97523,
97524,
97525,
97527,
97528,
97529]
    pulselist = list(arange(97560,97563))
    pulselist = [97512,
97509,
97510,
97511]
    pulselist = [97552,
97553,
97593,
97594,
97551]
    pulselist = [97536,
97537,
97539,
97540,
97541,
97542,
97543,
97544,
97545,
97555,
97531]
    pulselist = [
    97696,
    97697]
    pulselist = [97589,
    97685,
    97679]
    pulselist = [97680,
97674,
97586]
    pulselist = [97764,
97797,
97798,
97799,
97779,
97783,
97784,
97787,
97790]
    pulselist = [97799,97783,97787]
    pulselist = [97860,
97861,
97862,
97863,
97864,
97865,
97866,
97867,
97868,
97869,
97844,
97845,
97847,
97848,
97849,
97851,
97853]
    pulselist =arange(97866,97870)
    pulselist = [97860,
97861,
97862,
97863,
97864,
97865,
97844,
97845,
97847,
97848,
97849,
97851,
97853
]
    pulselist = [97897,
97898,
97899,
97900
]
    pulselist = [97952,
97953,
97949,
97950,
97951]
    pulselist = [97521,
97522,
97523,
97524,
97516,
97517,
97518]
    pulselist =[97516]
    pulselist =[97985,
97858,
97927,
97995,
97971,
98004,
98005,
97943,
97981 ]
    pulselist = [97761,
97765,
97758]
    for pulse in pulselist:
        readdata(pulse, "bviola")
    with open('pulselist.txt', 'w+') as f:
        for item in pulselist:
         f.write("%s\n" % item)
    upload_to_dropbox(pulselist,'saved')
    #download_from_dropbox(pulselist, 'saved')
