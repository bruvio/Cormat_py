"""
Class to read and store all kg4 data
"""

import logging

import numpy as np

from signal_base import SignalBase
from make_plots import make_plot
import pdb

logger = logging.getLogger(__name__)

# ----------------------------
__author__ = "L. Kogan"
# ----------------------------


class Kg4Data:
    # Conversion factor for calculating faraday rotation
    CIB = 51.6

    # Minimum faraday rotation angle below which signal is bad
    MIN_FAR = 0.02

    # ------------------------
    def __init__(self, constants):
        """
        Init function

        :param constants: instance of Kg1Consts class
        """
        self.constants = constants
        self.faraday = {}
        self.ellipticity = {}
        self.xg_elld_signal = {}
        self.xg_ell_signal = {}
        self.density = {}

        self.xg_ell_signal_start = 0
        self.xg_ell_signal_end = 0

    # ------------------------
    def _find_kg4_times(self):
        """
        Find the start and end time of
        the kg4

        :return: False if there is no kg4
                True otherwise

        """

        # First, find if there was a KG4 signal
        ind_first_ip = np.argmax(self.xg_ell_signal.data > self.MIN_IP)
        ip_reversed = self.ip.data[::-1]
        ind_last_ip = len(ip_reversed) - np.argmax(ip_reversed > self.MIN_IP) - 1

    # ------------------------
    def read_data(self, mag, shot_no):
        """
        Read in faraday angle & ellipticity, and convert to densities

        :param mag: Instance of MagData, with data read in already. Needed for conversion to density
        :param shot_no: shot number
        """
        # Read in faraday rotation angle and calculate density #NOT USED
        for far_chan in self.constants.kg4_far.keys():
            node_name = self.constants.kg4_far[far_chan]
            far_signal = SignalBase(self.constants)
            far_signal.read_data_jpf(node_name, shot_no)

            if far_signal.data is not None:
                # Keep points where there is ip
                far_signal.delete_points(
                    np.where(
                        (far_signal.time < mag.start_ip)
                        | (far_signal.time > mag.end_ip)
                    )
                )

                if len(far_signal.time) == 0:
                    continue

                # Remove bad data points
                far_signal.delete_points(np.where(far_signal.data < self.MIN_FAR))

                if len(far_signal.time) == 0:
                    continue

                # Calculate density based on faraday rotation angle
                ip = np.interp(far_signal.time, mag.ip.time, mag.ip.data)
                bvac = np.interp(far_signal.time, mag.bvac.time, mag.bvac.data)
                bvac *= self.CIB

                # This formula is not the "correct" formula for calculating the
                # density from the faraday angle (which depends on b_pol, that we don't have pre-EFIT), but
                # it is an empirical formula that was probably derived some time ago from statistical studies
                far_signal.data = -1.0 * np.tan(2 * far_signal.data) / (ip * bvac)

                self.faraday[far_chan] = far_signal

                if (
                    self.constants.plot_type == "dpi"
                    and "kg4_data" in self.constants.make_plots
                ):
                    make_plot(
                        [[far_signal.time, far_signal.data]],
                        xtitles=["time [sec]"],
                        ytitles=["density from faraday"],
                        colours=["blue"],
                        pformat=[1],
                        show=True,
                        title="KG4 density from Faraday angle. Chan {}".format(
                            far_chan
                        ),
                    )

        # Read in ellipticity and calculate density #NOT USED
        for ell_chan in self.constants.kg4_ell.keys():
            node_name = self.constants.kg4_ell[ell_chan]
            ell_signal = SignalBase(self.constants)
            ell_signal.read_data_jpf(node_name, shot_no)

            if ell_signal.data is not None:
                # Only keep points where there is ip
                ell_signal.delete_points(
                    np.where(
                        (ell_signal.time < mag.start_ip)
                        | (ell_signal.time > mag.end_ip)
                    )
                )

                if len(ell_signal.time) == 0:
                    continue

                # Calculate density based on ellipticity
                bvac = np.interp(ell_signal.time, mag.bvac.time, mag.bvac.data)
                ell_signal.data /= bvac * bvac

                self.ellipticity[ell_chan] = ell_signal

                if (
                    self.constants.plot_type == "dpi"
                    and "kg4_data" in self.constants.make_plots
                ):
                    make_plot(
                        [[ell_signal.time, ell_signal.data]],
                        xtitles=["time [sec]"],
                        ytitles=["density from ellipticity"],
                        colours=["blue"],
                        pformat=[1],
                        show=True,
                        title="KG4 density from ellipticity. Chan {}".format(ell_chan),
                    )

        # Read in status signal from Cotton Mutton effect
        for cm_chan in self.constants.kg4_xg_elld.keys():
            node_name = self.constants.kg4_xg_elld[cm_chan]
            xg_elld_signal = SignalBase(self.constants)
            xg_elld_signal.read_data_jpf(node_name, shot_no)
            self.xg_elld_signal[cm_chan] = xg_elld_signal
            if (
                self.constants.plot_type == "dpi"
                and "kg4_cmdata" in self.constants.make_plots
            ):
                make_plot(
                    [[xg_elld_signal.time, xg_elld_signal.data]],
                    xtitles=["time [sec]"],
                    ytitles=["status "],
                    colours=["blue"],
                    pformat=[1],
                    show=True,
                    title="KG4 Cotton Mutton status. Chan {}".format(cm_chan),
                )
            if xg_elld_signal.data is not None:
                if xg_elld_signal.data.all() == 1.0:
                    # if signal status is 1 than read density signal

                    dmsg = "KG4 CM status chan {} is ok".format(cm_chan)
                    logger.log(5, dmsg)
                    # pdb.set_trace()
                    # if xg_elld_signal.data is not None:
                    #     # Only keep points where there is ip
                    #     xg_elld_signal.delete_points(np.where(
                    #         (xg_elld_signal.time < mag.start_ip) | (
                    #                 xg_elld_signal.time > mag.end_ip)))
                    #     # DELETE POINTS WHERE BVAC <1.5T
                    #     xg_elld_signal.delete_points(
                    #         np.where((xg_elld_signal.time < mag.start_bvac) | (
                    #                 xg_elld_signal.time > mag.end_bvac)))
                    #     # DELETE POINTS WHERE IP <1MA
                    #     xg_elld_signal.delete_points(
                    #         np.where((xg_elld_signal.time < mag.start_ip1MA) | (
                    #                 xg_elld_signal.time > mag.end_ip1MA)))
                    #
                    #     #only keep points where status is 1
                    #     self.ind_first_statusok = np.argmax(
                    #         xg_elld_signal.data >= 1.0)
                    #     kg4status_reversed = xg_elld_signal.data[::-1]
                    #
                    #     self.ind_last_statusok = len(kg4status_reversed) - np.argmax(
                    #         kg4status_reversed >= 1.0) - 1
                    #
                    #     if len(xg_elld_signal.time) == 0:
                    #         continue
                    #
                    #     self.xg_elld_signal[cm_chan] = xg_elld_signal

                    # for cm_chan in self.constants.kg4_xg-ell.keys():
                    node_name1 = self.constants.kg4_xg_ell[cm_chan]
                    xg_ell_signal = SignalBase(self.constants)
                    xg_ell_signal.read_data_jpf(node_name1, shot_no)
                # pdb.set_trace()

                # node_name = self.constants.kg4_xg-ell[cm_chan]
                # cm_signal = SignalBase(self.constants)
                # dda = node_name[:node_name.find('/')]
                # dtype = node_name[node_name.find('/')+1:]
                # status = cm_signal.read_data_ppf(dda, dtype, shot_no, read_bad=True,
                #                                read_uid="JETPPF")

                if xg_ell_signal.data is not None:
                    # Only keep points where there is ip
                    xg_ell_signal.delete_points(
                        np.where(
                            (xg_ell_signal.time < mag.start_ip)
                            | (xg_ell_signal.time > mag.end_ip)
                        )
                    )
                    # DELETE POINTS WHERE BVAC <1.5T
                    xg_ell_signal.delete_points(
                        np.where(
                            (xg_ell_signal.time < mag.start_bvac)
                            | (xg_ell_signal.time > mag.end_bvac)
                        )
                    )
                    # DELETE POINTS WHERE IP <1MA
                    xg_ell_signal.delete_points(
                        np.where(
                            (xg_ell_signal.time < mag.start_ip1MA)
                            | (xg_ell_signal.time > mag.end_ip1MA)
                        )
                    )

                    if len(xg_ell_signal.data) == 0:
                        continue

                    self.xg_ell_signal[cm_chan] = xg_ell_signal

                    if (
                        self.constants.plot_type == "dpi"
                        and "kg4_cmdata" in self.constants.make_plots
                    ):
                        make_plot(
                            [[xg_ell_signal.time, xg_ell_signal.data * 1e18]],
                            xtitles=["time [sec]"],
                            ytitles=["density from Cotton Mutton"],
                            colours=["blue"],
                            pformat=[1],
                            show=True,
                            title="KG4 density from Cotton Mutton. Chan {}".format(
                                cm_chan
                            ),
                        )

        # Read in kg4r signal from ppf
        for kg4_chan in self.constants.kg4r.keys():
            nodename = self.constants.kg4r[kg4_chan]
            density = SignalBase(self.constants)
            dda = nodename[: nodename.find("/")]
            dtype = nodename[nodename.find("/") + 1 :]
            status = density.read_data_ppf(
                dda, dtype, shot_no, read_bad=True, read_uid="JETPPF"
            )

            if density.data is not None:
                self.density[kg4_chan] = density
