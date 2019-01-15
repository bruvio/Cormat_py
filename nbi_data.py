"""
Class to read in NBI data and store start & end of NBI power
"""

import logging

import numpy as np

from signal_base import SignalBase
from make_plots import make_plot

logger = logging.getLogger(__name__)

# ----------------------------
__author__ = "L. Kogan"
# ----------------------------


class NBIData:
    NBI_MIN_POWER = 3.5

    # ------------------------
    def __init__(self, constants):
        """
        Init function

        :param constants: Instance of Kg1Consts, including all constants
        """
        self.constants = constants
        self.start_nbi = 0.0
        self.end_nbi = 0.0

    # ------------------------
    def read_data(self, shot_no):
        """
        Read in nbi data

        :param shot_no: shot number
        """
        nodes = self.constants.nbi.values()

        nbi_start, nbi_end = self._read_and_get_times(nodes, shot_no)

        self.start_nbi = nbi_start
        self.end_nbi = nbi_end

        logger.debug("NBI start {}, NBI end {}".format(self.start_nbi, self.end_nbi))

    # ------------------------
    def _read_and_get_times(self, node_names, shot_no):
        """
        Read in an NBI signals, and find start and end times of the NBI

        :param node_names: jpf node names to read in
        :param shot_no: shot number
        :return: start_nbi, end_nbi
        """

        nbi_time = None
        nbi_data = None

        # We have to use the JPFs with power for each pini... so need to sum them to get total power
        # They also have different timebases, depending on when the pini starts/ends, so need to
        # put them all on the same timebase

        all_data = []
        all_time = []

        min_time = 999999
        max_time = 0.0

        # --------------------
        # Read in the power for each pini
        # --------------------
        for node in node_names:
            nbi_signal = SignalBase(self.constants)
            nbi_signal.read_data_jpf(node, shot_no)

            if nbi_signal.data is None:
                continue

            all_data.append(nbi_signal.data)
            all_time.append(nbi_signal.time)

            if nbi_signal.time[0] < min_time:
                min_time = nbi_signal.time[0]
            if nbi_signal.time[-1] > max_time:
                max_time = nbi_signal.time[-1]

        if len(all_data) == 0 or len(all_time) == 0:
            return 0.0, 0.0

        # --------------------
        # Each pini can have a different time-base: put all signals
        # on the same time-base and add the nbi data together
        # THIS ASSUMES THE TIME RESOLUTION IS CONSTANT FOR THE WHOLE SIGNAL!
        # --------------------
        time_res = np.mean(all_time[0][1:] - all_time[0][0:-1])

        n_points_total = round((max_time - min_time) / time_res) + 1

        nbi_time = np.arange(n_points_total) * time_res + min_time
        nbi_data = None

        for time, data in zip(all_time, all_data):
            n_start = int(round((time[0] - min_time) / time_res))
            n_end = int(round((max_time - time[-1]) / time_res))
            new_data = data

            if n_start > 0:
                # print(data)
                # print(int(n_start))
                # print(int(n_end))
                new_data = np.concatenate((np.zeros((n_start)), data))
            if n_end > 0:
                new_data = np.append(new_data, np.zeros(n_end))

            if nbi_data is None:
                nbi_data = new_data
            else:
                nbi_data += new_data

        ind_nbi = np.where(nbi_data > self.NBI_MIN_POWER)[0]

        if len(ind_nbi) == 0:
            return 0.0, 0.0

        if ind_nbi[-1] > len(nbi_data)-1:
            logger.warning("Index of end of NBI is > length of NBI data! No NBI times will be returned")
            return 0.0, 0.0

        start_nbi = nbi_time[ind_nbi[0]]
        end_nbi = nbi_time[ind_nbi[-1]]

        if start_nbi < 10.0:
            return 0.0, 0.0

        if "dpi" in self.constants.plot_type and "nbi_data" in self.constants.make_plots:
            make_plot([[nbi_time, nbi_data]], vert_lines=[[start_nbi, end_nbi]], show=True,
                      title="NBI power (blue) and start / end NBI (red lines)")

        return start_nbi, end_nbi
