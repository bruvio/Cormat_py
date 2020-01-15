# -*- coding: utf-8 -*-
"""
 Simple program to access status flags
 contains a main that creates a database for a given pulse list
"""
# ----------------------------
__author__ = "B. Viola"
# ----------------------------
from ppf import *
import csv
import sys
import collections
import matplotlib.pyplot as plt
import argparse
import numpy as np
from getdat import getdat, getsca

# from make_plots import make_plots

# import pylab as P
from scipy import array, zeros
import os
import sys

path = os.getcwd()
# print(path)
# sys.path.append("/jet/share/lib/python")
import logging

logger = logging.getLogger(__name__)


def _log_level_string_to_int(log_level_string):
    if not log_level_string in _LOG_LEVEL_STRINGS:
        message = "invalid choice: {0} (choose from {1})".format(
            log_level_string, _LOG_LEVEL_STRINGS
        )
        raise argparse.ArgumentTypeError(message)

    log_level_int = getattr(logging, log_level_string, logging.INFO)
    # check the logging log_level_choices have not changed from our expected values
    assert isinstance(log_level_int, int)

    return log_level_int


def find_disruption(pulse):
    """

    given a pulse return if it has disrupted (True) or not (False) \
    returns n/a if there is no information about disruptions
    :param pulse:
    :return: boolean

    """
    # print(pulse)
    data, nwds, title, units, ier = getsca("PF/PTN-DSRPT<PFP", pulse, nwds=0)
    # print(shape(data))
    # print(dtype(data))
    # print(pulse,data,ier)
    ###print(len(data))
    if int(ier) == 0:
        if data[0] > 0.0:
            return "True"
        else:
            return "False"
    else:
        return "n/a"


def initread():
    """

    initialize ppf
    :return:
    """
    # ier=ppfgo(pulse,sequence)
    # ppfsetdevice("JET")
    ppfuid("jetppf", "r")
    # ppfuid("bviola","r")
    ppfssr(i=[0, 1, 2, 3, 4])


def GetSF(pulse, dda, dtype):
    """
    
    :param pulse:
    :param dda: string e.g. 'kg1v'
    :param dtype: string e.g. 'lid3'
    :return: SF := status flag
    """

    # this sequence of instruction allows to extract status flag correctly for each pulse
    ihdat, iwdat, data, x, t, ier = ppfget(pulse, dda, dtype)
    pulse, seq, iwdat, comment, numdda, ddalist, ier = ppfinf(comlen=50, numdda=50)
    # info,cnfo,ddal,istl,pcom,pdsn,ier=pdinfo(pulse,seq) #commented lines, with this i get an error.
    istat, ier = ppfgsf(pulse, seq, dda, dtype, mxstat=1)

    # print('GETSF ok')

    return istat


def Getnonvalidatedpulses(pulselist, dtypelist, SF_validated):
    """
    
    
    
    :param pulselist: list of pulses
    :param dtypelist: string e.g. 'lid1','lid2',...
    :param SF_validated: integer rapresenting SF for validated shots
    :return: array of integer with pulse numbers,status flag list
    """

    pulses_ok = list()
    data_SF_list = list()
    isdisruption = list()
    for j in pulselist:
        data_SF = list()
        pulse = j
        pulseok = True
        # print(pulse)
        distrupted = find_disruption(pulse)
        for i in range(0, len(dtypelist)):

            ddatype = str(dtypelist[i])

            aa = GetSF(pulse, "kg1v", ddatype)
            # print(aa)
            data_SF.append(np.asscalar(aa))
        logger.debug("printing data_SF for pulse %d", pulse)
        logger.debug("status flag are %s", data_SF)
        logger.debug("")
        for item in data_SF:
            if item in SF_validated:
                pulseok = False
                break
            else:
                pass

        if pulseok:
            # print(pulse)
            pulses_ok.append(pulse)
            logger.info("pulse %d has disrupted %s", pulse, distrupted)
            isdisruption.append(distrupted)
            data_SF_list.append(data_SF)
            logger.info("pulse %d has NOT been validated", pulse)
            logger.info("data_Sf for non validated pulse are %s", data_SF)
            logger.info("status flag is set to %r", pulseok)
        else:
            logger.info(
                "pulse %d has been validated", pulse,
            )
            logger.info("data_SF for validated pulse are %s", data_SF)
            logger.info("status flag is set to %r", pulseok)
        # print('Getnonvalidatedpulses ok')
    return pulses_ok, data_SF_list, isdisruption


def GETfringejumps(pulse, FJC_dtypelist):
    """

    :param pulse: pulse number
    :param FJC_dtypelist: string e.g. 'FC1','FC2',...
    :return: array of integer, rapresenting fringe jumps corrections
    """

    FJ_correction = list()
    for jj in range(0, len(FJC_dtypelist)):
        FJcount = FJC_dtypelist[jj]
        ihdat, iwdat, data, x, t, ier = ppfget(pulse, "KG1V", FJcount)
        corrections = iwdat[3]
        FJ_correction.append(corrections)

    return FJ_correction


# if __name__ == '__main__':


def main(pulse1, pulse2, FJthres, outputfilename):
    """
    :param pulse1:intial pulse
    :param pulse2: final pulse
    :param FJthres: threshold to be used to check number of fringe jumps in pulse
    :param outputfilename: output database name
    :return: database containing all pulses inside the given interval whose median of fringe jumps \
exceed the given threshold and marks if there was a disruption or not
    """

    logger.info("start")
    initread()
    maxpulse = pdmsht()

    logger.info("checking pulse list")
    if pulse2 < maxpulse:
        pulseSpec = range(pulse1, pulse2)
    if pulse2 > maxpulse:
        logger.info("pulse2 is greater that max pulse")
        sys.exit("pulse2 is greater than max pulse")
    if pulse2 < pulse1:
        logger.info("pulse2 is greater that pulse1")
        sys.exit("pulse2 is greater that pulse1")

    filename = outputfilename + "_" + str(pulse1) + "_" + str(pulse2)

    #
    ier = ppfgo()
    ppfsetdevice("JET")
    ppfuid("jetppf", "r")
    # ppfuid("bviola","r")
    ppfssr(i=[0, 1, 2, 3])

    dda = "KG1V"

    LID_dtype = ["LID1", "LID2", "LID3", "LID4", "LID5", "LID6", "LID7", "LID8"]
    FJC_dtype = ["FC1", "FC2", "FC3", "FC4", "FC5", "FC6", "FC7", "FC8"]
    SF_validated = [1, 2, 3]
    logger.info("getting non validated pulse list")
    # try:
    pulses, data_SF, isdisruption = Getnonvalidatedpulses(
        pulseSpec, LID_dtype, SF_validated
    )
    # print(pulses,data_SF)
    # logger.debug("done")
    # except    :

    # sys.exit('failed to get non validated pulses')
    logger.info("checking if not validated pulses have a lot of FJ")
    goodpulses = {}
    goodpulses.setdefault("JPN", [])
    goodpulses.setdefault("disruption", [])
    goodpulses.setdefault("SF1", [])
    goodpulses.setdefault("SF2", [])
    goodpulses.setdefault("SF3", [])
    goodpulses.setdefault("SF4", [])
    goodpulses.setdefault("SF5", [])
    goodpulses.setdefault("SF6", [])
    goodpulses.setdefault("SF7", [])
    goodpulses.setdefault("SF8", [])
    goodpulses.setdefault("FJ1", [])
    goodpulses.setdefault("FJ2", [])
    goodpulses.setdefault("FJ3", [])
    goodpulses.setdefault("FJ4", [])
    goodpulses.setdefault("FJ5", [])
    goodpulses.setdefault("FJ6", [])
    goodpulses.setdefault("FJ7", [])
    goodpulses.setdefault("FJ8", [])
    logger.info("defining output matrix")
    for h, shot in enumerate(pulses):

        fjcorrection = GETfringejumps(shot, FJC_dtype)
        # print(fjcorrection)
        if np.median(fjcorrection) > FJthres:
            logger.info("found unvalidated pulse with FJs: %d", shot)
            logger.info("found unvalidated pulse with FJs: %d", shot)
            logger.info("it" "s SF are %s: ", data_SF)
            logger.info("FJ correction applied are %s", str(fjcorrection))
            logger.info("median of FJ %f ", np.median(fjcorrection))

            goodpulses["JPN"].append(shot)
            goodpulses["disruption"].append(isdisruption[h])
            goodpulses["SF1"].append(data_SF[h][0])
            goodpulses["SF2"].append(data_SF[h][1])
            goodpulses["SF3"].append(data_SF[h][2])
            goodpulses["SF4"].append(data_SF[h][3])
            goodpulses["SF5"].append(data_SF[h][4])
            goodpulses["SF6"].append(data_SF[h][5])
            goodpulses["SF7"].append(data_SF[h][6])
            goodpulses["SF8"].append(data_SF[h][7])
            goodpulses["FJ1"].append(fjcorrection[0])
            goodpulses["FJ2"].append(fjcorrection[1])
            goodpulses["FJ3"].append(fjcorrection[2])
            goodpulses["FJ4"].append(fjcorrection[3])
            goodpulses["FJ5"].append(fjcorrection[4])
            goodpulses["FJ6"].append(fjcorrection[5])
            goodpulses["FJ7"].append(fjcorrection[6])
            goodpulses["FJ8"].append(fjcorrection[7])
        else:
            logger.info("unvalidated pulse %d does not have FJs", shot)
            # logger.info('unvalidated pulse  %d does not have FJs',shot)
            logger.debug("data_SF %s: ", data_SF)
            logger.debug("fjcorrection %s", str(fjcorrection))
    goodpulses_sorted = collections.OrderedDict(sorted(goodpulses.items()))
    # aaa=
    logger.info("writing to file")
    try:
        with open(path + "/" + filename + ".csv", "w") as f:  # Just use 'w' mode in 3.x
            c = csv.writer(f)
            for key, value in goodpulses_sorted.items():
                c.writerow([key] + value)
        f.close()

    except:
        sys.exit("error writing to file")
    logger.info("pulse list written to file %s", path + "/" + filename + ".csv")
    logger.info("end")


def printdict(goodpulses_sorted):
    w = csv.writer(
        sys.stdout, delimiter="\t", quoting=csv.QUOTE_NONE, lineterminator="\n"
    )
    w.writerows(goodpulses_sorted.values())


if __name__ == "__main__":
    # Ensure we are running python 3
    # assert sys.version_info >= (3,3), "Python version too old. Please use >= 3.3.X."
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s \t %(levelname)s \t %(message)s",
        filename=path + "/debug.log",
        filemode="w",
    )
    _LOG_LEVEL_STRINGS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
    # Parse arguments from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p1", "--pulse1", type=int, help="start pulse number to run.", required=True
    )
    parser.add_argument(
        "-p2", "--pulse2", type=int, help="last pulse to check.", required=True
    )
    parser.add_argument(
        "-f", "--FJthres", type=int, help="fringe jumps threshold.", default=30
    )
    parser.add_argument(
        "-n", "--outputfilename", type=str, help="output filename.", default="output"
    )

    parser.add_argument(
        "-d",
        default="INFO",
        dest="log_level",
        type=_log_level_string_to_int,
        nargs="?",
        help="Set the logging output level. {0}".format(_LOG_LEVEL_STRINGS),
    )

    args = parser.parse_args(sys.argv[1:])

    logger = logging.getLogger(__name__)
    logger.setLevel(args.log_level)

    # Call the main code
    main(args.pulse1, args.pulse2, args.FJthres, args.outputfilename)
