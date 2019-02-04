"""
Class to read and store time of pellets.

Expecting to use PL/PTRK-ANA<PKM signal, which has a data point
per pellet, the value of which is the mass of the pellet in mg,
measured using a microwave cavity.
"""

import logging

import numpy as np

from signal_base import SignalBase
from make_plots import make_plot

logger = logging.getLogger(__name__)

# ----------------------------
__author__ = "L. Kogan"
# ----------------------------


class PelletData:
    # Pellet threshold (mass above which we want to worry about there being a pellet)
    # Smaller pellets don't give a significant density jump, so we don't care so much.
    PELLET_THRESHOLD = 4.0

    # ------------------------
    def __init__(self, constants):
        """
        Init function

        :param constants: Kg1Consts
        """
        self.constants = constants
        self.n_pellets = 0
        self.time_pellets = None

    # ------------------------
    def read_data(self, shot_no):
        """
        Read in pellets data

        :param shot_no: Shot number
        """
        pellet_signal = None

        # Read in the first available pellet signal
        for pellet_chan in self.constants.pellets.keys():
            node_name = self.constants.pellets[pellet_chan]
            pellet_signal = SignalBase(self.constants)
            pellet_signal.read_data_jpf(node_name, shot_no)

            if pellet_signal.data is not None:
                break

        if pellet_signal.data is None:
            return

        # Look for time points where the pellet mass is above threshold
        ind_pellet = np.where(pellet_signal.data > self.PELLET_THRESHOLD)

        if len(ind_pellet[0]) == 0:
            return

        self.n_pellets = len(ind_pellet[0])
        self.time_pellets = pellet_signal.time[ind_pellet]

        logger.debug("Read in pellets, {} were found/".format(self.n_pellets))

        if self.constants.plot_type == "dpi" and "pellet_data" in self.constants.make_plots:
            make_plot([[pellet_signal.time, pellet_signal.data]], ytitles=["pellet mass [mg]"],
                      vert_lines=[self.time_pellets], show=True,
                      title="Pellet signal (blue) and time of pellets (red lines)")

