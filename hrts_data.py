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
    def read_data(self, shot_no, read_uid="JETPPF"):
        """
        Read in HRTX data


        :param shot_no: shot number
        """

        for hrts_chan in self.constants.hrts.keys():
            node_name = self.constants.hrts[hrts_chan]
            hrts_signal = SignalBase(self.constants)
            dda = node_name[:node_name.find('/')]
            dtype = node_name[node_name.find('/') + 1:]
            status = hrts_signal.read_data_ppf(dda, dtype, shot_no, read_bad=True,
                                           read_uid=read_uid)
            # status = hrts_signal.read_data_ppf(self, dda, dtype, int(shot_no), seq=0,read_uid)
            # hrts_signal.read_data_ppf(self, dda, dtype, shot_no, read_uid="JETPPF", seq=0)

            if hrts_signal.data is not None:

                        
             self.density[hrts_chan] = hrts_signal

                

