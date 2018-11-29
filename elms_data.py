"""
Class to read Be-II signals, and detect ELMs.

The disruption time can be specified, in which case only ELMs before this time will be detected

Method used for ELM detection:

  -  Only use the Be-II signal up until the disruption time, if there is a disruption.
     This ensures that the filtering doesn't give us extra unwanted oscillations due
     to the large signal at the time of the disruption.
  -  Find the background using wavelet filtering (module wv_get_background).
  -  Find ELMs by studying the first derivative of the Be-II signal. We are looking for a positive derivative, followed by a negative derivative. Different thresholds can be set for the positive & negative derivative to account for the shape of the ELM signals (sharp rise, followed by shallower fall off).

Future improvements:
  - Finding the background using wavelets is a bit slow: try a moving average
  - a variable threshold. Sometimes the threshold is too low/high, resulting in incorrectly detected ELMs or missing ELMs.

"""

import collections
import logging

import numpy as np

from signal_base import SignalBase
from wv_denoise import wv_denoise
from wv_get_background import wv_get_background
from make_plots import make_plot

logger = logging.getLogger(__name__)

# ----------------------------
__author__ = "L. Kogan"
# ----------------------------


class ElmsData:
    """
    Class to read Be-II signals, and detect ELMs. 
    """

    # Constants for filtering data
    WV_FAMILY = 'db15'
    WV_PERC = 99.0
    START_TIME = 40.0  # This is used when finding the background
    END_TIME = 65.0  # This is used when finding the background

    # Thresholds on the first derivative for ELM finding
    UP_THRESH = 0.5
    DOWN_THRESH = -0.3

    # The maximum width permitted for an ELM, above this it won't be counted
    ELM_WIDTH_MAX = 0.1

    # This is used to get rid of the large spike at the beginning of the Be-II
    # JPF signals, after this the data should be valid
    BE_START_TIME = 35.0

    # ------------------------
    def __init__(self, constants, shot_no, dis_time=0.0):
        """
        Init function

        :param constants: instance of Kg1Consts class
        :param shot_no: shot number
        :param dis_time: Time of disruption, set to zero for no disruption.
                         Elms are only detected before dis_time.

        """
        self.constants = constants
        self.n_elms = 0
        self.time_elms = None

        self._find_elms(shot_no, dis_time)

    # ------------------------
    def _find_elms(self, shot_no, dis_time):
        """
        Read in ELMs signal and find elms

        :param shot_no: shot number
        :param dis_time: Disruption time. Set to zero for no disruption. ELMs will only be detected before this time.
        """

        # Sort the python dict according to the keys
        # This means the signals are in the order listed in the config file.
        node_names = collections.OrderedDict(sorted(self.constants.elms.items()))
        elms_signal = SignalBase(self.constants)

        # Read in the first valid JPF signal
        for node_name in node_names.values():
            elms_signal.read_data_jpf(node_name, shot_no)

            if elms_signal.data is not None:
                logger.log(5, "Using {} for finding ELMs.".format(node_name))
                break

        if elms_signal.data is None:
            logger.debug(5, "No signal was found for ELM finding.")
            return

        # If there is a disruption, only use signal up until dis_time
        if dis_time > 0:
            ind_analyse = np.where(elms_signal.time < dis_time)
            if np.size(ind_analyse) > 0:
                elms_signal.time = elms_signal.time[ind_analyse]
                elms_signal.data = elms_signal.data[ind_analyse]

        # Get rid of the large spike you get at the beginning of the JPF Be-II signals
        ind_analyse = np.where(elms_signal.time > self.BE_START_TIME)
        if np.size(ind_analyse) > 0:
            elms_signal.time = elms_signal.time[ind_analyse]
            elms_signal.data = elms_signal.data[ind_analyse]

        # Subtract the background. The background is found using wavelet filtering.
        background = wv_get_background(elms_signal.time, elms_signal.data, self.START_TIME, self.END_TIME)
        data_sub_back = elms_signal.data - background

        # Filter the data
        data_filt = wv_denoise(data_sub_back, family=self.WV_FAMILY, percent=self.WV_PERC)

        # Calculate the first derivative
        first_deriv = data_filt[10:] - data_filt[0:-10]

        if self.constants.plot_type == "dpi" and "elms_data" in self.constants.make_plots:
            make_plot([[elms_signal.time, elms_signal.data], [elms_signal.time, data_filt],
                       [elms_signal.time[0:-10], first_deriv]],
                      labels=["be-II", "filt", "1st deriv"], colours=["blue", "green", "green"],
                      pformat=[3, 1],
                      show=True, horz_lines=[[], [self.UP_THRESH, self.DOWN_THRESH]],
                      title="Be-II signal for ELM finding, and 1st derivative of Be-II signal")

        # Find ELMs

        # Look for start and end of ELMs, by placing cuts on the first derivative
        pass_up_thresh = np.zeros(data_filt.shape)
        ind_up = np.where(first_deriv > self.UP_THRESH)
        pass_up_thresh[ind_up] = 1
        pass_up_diff = pass_up_thresh[1:] - pass_up_thresh[0:-1]

        pass_down_thresh = np.zeros(data_filt.shape)
        ind_down = np.where(first_deriv < self.DOWN_THRESH)
        pass_down_thresh[ind_down] = 1
        pass_down_diff = pass_down_thresh[1:] - pass_down_thresh[0:-1]

        ind_start = np.where(pass_up_diff > 0)[0]
        ind_end = np.where(pass_down_diff < 0)[0]

        # Loop over possible ELMs
        elm_times = np.arange(0)

        skip_next = 0

        if len(ind_start) == 0 or len(ind_end) == 0:
            logger.debug("No ELMs were found.")
            self.n_elms = 0
            self.time_elms = None
            return

        for index, poss_start in enumerate(ind_start):
            if skip_next > 0:
                skip_next -= 1
                continue

            # Find the next downwards derivative
            ind_after, = np.where(ind_end > poss_start)

            if np.size(ind_after) == 0:
                continue

            index_end = np.min(ind_after)
            poss_end = ind_end[index_end]

            # Impose a maximum ELM width
            time_diff = elms_signal.time[poss_end] - elms_signal.time[poss_start]

            if time_diff > self.ELM_WIDTH_MAX:
                continue

            # Make sure we don't count any more between poss_start and poss_end
            ind_skip, = np.where((ind_start > poss_start) & (ind_start < poss_end))

            skip_next = np.size(ind_skip)

            # Add ELM time to list of elm times
            elm_times = np.append(elm_times, elms_signal.time[poss_start])

        # Store the number and times of the elms.
        if np.size(elm_times) > 0:
            self.time_elms = elm_times
            self.n_elms = np.size(elm_times)
            logger.debug("{} ELMs were found.".format(self.n_elms))

            if self.constants.plot_type == "dpi" and "elms_data" in self.constants.make_plots:
                make_plot([[elms_signal.time, elms_signal.data], [elms_signal.time, data_filt],
                           [elms_signal.time[0:-10], first_deriv],
                           [elms_signal.time, elms_signal.data], [elms_signal.time, elms_signal.data]],
                           labels=["Be-II", "filt", "1st deriv", "starts", "ends"],
                           colours=["blue", "green", "green", "blue", "blue"],
                           pformat=[2, 1, 1, 1],
                           show=True,
                           vert_lines=[elm_times, [], elms_signal.time[ind_start], elms_signal.time[ind_end]],
                           horz_lines=[[], [self.UP_THRESH, self.DOWN_THRESH],[],[]],
                           title="Be-II signal & 1st derivative used for ELM finding, detected elm times shown.")
