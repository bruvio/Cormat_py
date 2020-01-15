"""
Class to read and store magnetics data
"""

import logging

import numpy as np

from signal_base import SignalBase
from make_plots import make_plot

logger = logging.getLogger(__name__)

# ----------------------------
__author__ = "L. Kogan"
# ----------------------------


class MagData:
    # Minimum ip plasma must reach for it to be considered that there was a plasma current
    # If this is not reached then the maximum ip will be used to find the start and end of the ip
    MIN_IP = 0.3  # MA

    # Percentage of ip above which the plasma is considered to have reached the flattop
    PER_IP_FLAT = 0.8

    # For calculating bvac from average toroidal coil current
    CBVAC = 5.1892e-5

    # Minimum Bvac must reach for KG4 data to be considered
    MIN_BVAC = -1.5  # T

    # ------------------------
    def __init__(self, constants):
        """
        Init function

        :param constants: instance of Kg1Consts class

        """
        self.constants = constants

        self.ip = None
        self.start_ip = 0
        self.end_ip = 0
        self.start_flattop = 0
        self.end_flattop = 0

        self.start_ip1MA = 0
        self.end_ip1MA = 0
        self.start_bvac = 0
        self.end_bvac = 0

        self.bvac = None
        self.eddy_current = None

    # ------------------------
    def read_data(self, shot_no):
        """
        Read in magnetics data

        :param shot_no: shot number
        :returns: True if data was read successfully and there is ip
                  False otherwise.

        """
        # Read in Ip
        node_name = self.constants.magnetics["ip"]
        ip = SignalBase(self.constants)
        ip.read_data_jpf(node_name, shot_no)

        if ip.data is None:
            return False

        # Make ip positive, and convert from A to MA
        ip.data = np.absolute(ip.data) / 1e6
        self.ip = ip

        # Find times of ip
        if not self._find_ip_times():
            return False

        # Read in bvac
        node_name = self.constants.magnetics["bt_coil_current_av"]
        bvac = SignalBase(self.constants)
        bvac.read_data_jpf(node_name, shot_no)

        # Find times of ip

        # Read in eddy currents
        node_name = self.constants.magnetics["eddy_current"]
        eddy_current = SignalBase(self.constants)
        eddy_current.read_data_jpf(node_name, shot_no)

        # Store bvac and eddy currents
        if bvac.data is not None:
            bvac.data *= self.CBVAC
            self.bvac = bvac

        if not self._find_bvac_times():
            return False

        if eddy_current is not None:
            eddy_current.data *= -1.0
            self.eddy_current = eddy_current

        return True

    # ------------------------
    def _find_ip_times(self):
        """
        Find the start and end time of
        the ip and the flat-top.

        :return: False if there is no IP
                True otherwise

        """

        logger.debug(
            "Max ip : {}, Min ip allowed: {}".format(max(self.ip.data), self.MIN_IP)
        )

        # First, find if there was an ip above MIN_IP.
        ind_first_ip = np.argmax(self.ip.data > self.MIN_IP)
        ip_reversed = self.ip.data[::-1]
        ind_last_ip = len(ip_reversed) - np.argmax(ip_reversed > self.MIN_IP) - 1

        # Next, find the flat top
        ind_first_flat = np.argmax(
            self.ip.data > self.PER_IP_FLAT * np.max(self.ip.data)
        )
        ind_last_flat = (
            len(ip_reversed)
            - np.argmax(ip_reversed > self.PER_IP_FLAT * np.max(self.ip.data))
            - 1
        )

        # find where ip above 1MA
        ind_first_ip1MA = np.argmax(self.ip.data >= 1.0)
        ind_last_ip1MA = len(ip_reversed) - np.argmax(ip_reversed >= 1.0) - 1

        # Check for cases where there was barely any Ip.
        if ind_first_ip == 0 and ind_last_ip == len(self.ip.time) - 1:
            return False

        if ind_first_ip == 0 and (ind_last_ip - ind_first_ip) >= 100:
            ind_last_ip = len(self.ip.data) - 1

            # If there was no ip above min_ip, and there was current for > 0.1 s
            max_ip = self.ip.data[ind_first_flat - 100]
            ind_first_flat = np.argmax(self.ip.data > self.PER_IP_FLAT * max_ip)
            ind_last_flat = (
                len(ip_reversed)
                - np.argmax(ip_reversed > self.PER_IP_FLAT * max_ip)
                - 1
            )

        elif ind_first_ip == 0:
            return False

        # Set times of start and end ip (just before and after ind_first_ip and ind_end_ip)
        self.start_ip = self.ip.time[ind_first_ip] - 1e-4
        self.end_ip = self.ip.time[ind_last_ip] + 1e-4
        # Set times of start and end ip > 1 MA (just before and after ind_first_ip1MA and ind_end_ip1MA)
        self.start_ip1MA = self.ip.time[ind_first_ip1MA] - 1e-4
        self.end_ip1MA = self.ip.time[ind_last_ip1MA] + 1e-4

        # Set times of start and end of the flat top
        self.start_flattop = self.ip.time[ind_first_flat]
        self.end_flattop = self.ip.time[ind_last_flat]

        dmsg = "Start of Ip : {}, end of Ip : {}, start of flat-top {}, end of flat-top {}, |Ip| < 1MA {} - {}, Ip".format(
            self.start_ip,
            self.end_ip,
            self.start_flattop,
            self.end_flattop,
            self.start_ip1MA,
            self.end_ip1MA,
        )
        logger.debug(dmsg)

        # For debugging, plot ip and times of ip
        if (
            self.constants.plot_type == "dpi"
            and "mag_data" in self.constants.make_plots
        ):
            make_plot(
                [[self.ip.time, self.ip.data]],
                xtitles=["time [sec]"],
                ytitles=["ip [MA]"],
                vert_lines=[
                    [self.start_ip, self.start_flattop, self.end_flattop, self.end_ip]
                ],
                show=True,
                title="Ip (blue) and start / end ip and flat-top (red lines)",
            )

        return True

    # ------------------------
    def _find_bvac_times(self):
        """
        Find the start and end time of
        the Bvac > 1.5T

        :return: False if there is no Bvac
                True otherwise

        """

        logger.debug(
            "Max Bvac : {}, Min Bvac allowed: {}".format(
                min(self.bvac.data), self.MIN_BVAC
            )
        )

        # First, find if there was an ip above MIN_BVAC.
        ind_first_bvac = np.argmax(self.bvac.data < self.MIN_BVAC)
        bvac_reversed = self.bvac.data[::-1]
        ind_last_bvac = (
            len(bvac_reversed) - np.argmax(bvac_reversed < self.MIN_BVAC) - 1
        )

        # Check for cases where there was barely any Ip.
        if ind_first_bvac == 0 and ind_last_bvac == len(self.bvac.time) - 1:
            return False

        # Set times of start and end Bvac
        self.start_bvac = self.bvac.time[ind_first_bvac] - 1e-4
        self.end_bvac = self.bvac.time[ind_last_bvac] + 1e-4

        dmsg = "Start of Bvac < -1.5T : {}, end of Bvac < -1.5T : {}".format(
            self.start_bvac, self.end_bvac
        )
        logger.debug(dmsg)

        # For debugging, plot ip and times of ip
        if (
            self.constants.plot_type == "dpi"
            and "mag_data" in self.constants.make_plots
        ):
            make_plot(
                [[self.bvac.time, self.bvac.data]],
                xtitles=["time [sec]"],
                ytitles=["Bvac [T]"],
                vert_lines=[[self.start_bvac, self.end_bvac]],
                show=True,
                title="Bvac (blue) and start / end Bvac < -1.5T (red lines)",
            )

        return True
