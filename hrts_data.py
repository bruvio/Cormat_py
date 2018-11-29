"""
Class to read and store all hrts data
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


class HRTSData:

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
    def read_data(self, shot_no):
        """
        Read in faraday angle & ellipticity, and convert to densities

        :param mag: Instance of MagData, with data read in already. Needed for conversion to density
        :param shot_no: shot number
        """
        # Read in faraday rotation angle and calculate density #NOT USED
        for hrts_chan in self.constants.hrts.keys():
            node_name = self.constants.hrts[far_chan]
            hrts_signal = SignalBase(self.constants)
            hrts_signal.read_data_jpf(node_name, shot_no)

            if hrts_signal.data is not None:
                # Keep points where there is ip
                        
             self.density[hrts_chan] = hrts_signal

                

