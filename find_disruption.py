"""
Code to read in disruption JPF and check
for a disruption. Set the time-dependent status flags for the KG1
signals to 3 around the disruption.

Returns a boolean to say if there was a disruption or not.
Also returns two times: [disruption time - disruption window, disruption time + disruption window]

The rest of the KG1 code will not attempt to make any corrections within this time window.
"""

import logging

import numpy as np

from signal_base import SignalBase

logger = logging.getLogger(__name__)

# ----------------------------
__author__ = "L. Kogan"
# ----------------------------

def find_disruption(shot_no, constants, kg1_signals=None):
    """
    Find the disruption time from the JPF disruption signal

    :param shot_no: shot number
    :param constants: Instance of Kg1Consts, contains JPF node names and size of time window around disruption to exclude.
    :param kg1_signals: Instance of Kg1Data
    :return: Boolean for whether there was a disruption, [start disruption window, end disruption window]
    """

    # Read in disruption signal and extract disruption time (if there was one)
    dis_node = constants.disruption

    disruption_signal = SignalBase(constants)
    disruption_signal.read_data_jpf_1D(dis_node, shot_no)

    if disruption_signal.data is None:
        return False, [-1.0,-1.0]

    # Set the disruption window
    dis_window = [disruption_signal.data[0] - constants.dis_window,
                  disruption_signal.data[0] + constants.dis_window]

    # Set the status flag around the disruption time to 4 for all kg1_signals
    if kg1_signals is not None:
        for chan in kg1_signals.status.keys():
            # Set status to 3
            kg1_signals.set_status(chan, 3, time=dis_window)

    logger.log(5, "There was a disruption at {}, window is {}-{}.".format(disruption_signal.data[0],
                                                                          dis_window[0], dis_window[1]))

    return True, dis_window
