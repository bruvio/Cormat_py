"""
Class to read and store all lidar data
"""

import logging

import numpy as np

from signal_base import SignalBase
from make_plots import make_plot
import pdb

logger = logging.getLogger(__name__)

# ----------------------------
__author__ = "B. VIOLA"
# ----------------------------


class LIDARData:

    # ------------------------
    def __init__(self, constants):
        """
        Init function
        
        :param constants: instance of Kg1Consts class
        """
        self.constants = constants
        # density
        self.density = {}

        # ------------------------

    def read_data(self, shot_no, read_uid="JETPPF"):
        """
            Read in lidar (LIDX)
            

            :param shot_no: shot number
            """
        # Read in lidar
        for lidar_chan in self.constants.lidar.keys():
            node_name = self.constants.lidar[lidar_chan]
            lidar_signal = SignalBase(self.constants)
            dda = node_name[: node_name.find("/")]
            dtype = node_name[node_name.find("/") + 1 :]

            status = lidar_signal.read_data_ppf(
                dda, dtype, shot_no, read_bad=True, read_uid=read_uid
            )
            # status = lidar_signal.read_data_ppf(self, dda, dtype, shot_no,read_uid)
            # lidar_signal.read_data_ppf(self, dda, dtype, shot_no, read_uid="JETPPF", seq=0)

            if lidar_signal.data is not None:
                # Keep points where there is ip

                self.density[lidar_chan] = lidar_signal
