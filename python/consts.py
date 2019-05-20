"""
Class for reading in and storing kg1 constants,
signal names etc. 
"""

# ----------------------------
__author__ = "L. Kogan"
# ----------------------------

import configparser
import logging

import numpy as np

logger = logging.getLogger(__name__)

class Consts:

    # Fringe in terms of density for DCN & MET
    DFR_DCN = 1.14300e19  # phase->fj conversion factor for dcn
    DFR_MET = 1.876136e19  # phase->fj conversion factor for met

    # Constants for converting DCN & MET signals into density & mirror movement
    MAT11 = 0.9088193e19
    MAT12 = -0.5536807e19
    MAT21 = 0.5754791e-4
    MAT22 = -0.9445996e-4

    # Lateral channel correction matrices
    CORR_NE = np.array([-0.56e19, 0.91e19,  # Density in m^2
               0.35e19, 1.46e19,
               2.58e19, 2.02e19,
               -0.21e19, -0.76e19,
               3.49e19, 2.37e19,
               1.26e19, 0.15e19,
               3.84e19, 3.28e19,
               2.17e19, 1.61e19])

    CORR_VIB = np.array([-95.13e-6, 57.7e-6, -37.4e-6, 152.8e-6, 343.8e-6, 247.9e-6, -132.6e-6,  # Vib in m
                -227.7e-6, 400.7e-6, 210.5e-6, 20.2e-6, -170.0e-6, 363.3e-6, 268.2e-6,
                77.9e-6, -17.2e-6])

    FJ_DCN = np.array([0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3])  # Number fringes in DCN laser
    FJ_MET = np.array([1, 0, 1, -1, -3, -2, 2, 3, -3, -1, 1, 3, -2, -1, 1, 2])  # Number fringes in MET laser

    # jXb factors, for calculating estimated mirror movement due to JXB
    JXB_FAC = [-1.6e-5, -3.0e-5, -4.5e-5, -3.0e-5]

    # ------------------------
    def __init__(self, config_name, code_version):
        """
        Init function

        :param config_name: name of the configuration file
        """
        # This is used to determine in which modules plots are displayed. (For debugging!)
        self.make_plots = ""
        self.plot_type = ""

        # Version of the code
        self.code_version = int(float(code_version))

        # Important times
        self.time_ip = {"start_ip": 0.0,
                        "start_topip": 0.0,
                        "start_nbi": 0.0,
                        "end_nbi": 0.0,
                        "end_topip": 0.0,
                        "end_ip": 0.0}

        # Define constants to be read from file that have defaults

        # Valid CPRB (laser frequency) values and ranges for KG1C
        self.cprb_mid_dcn = 100
        self.cprb_mid_met = 23
        self.cprb_range_dcn = 2
        self.cprb_range_met = 2

        # Min amplitude for KG1R
        self.min_amp_kg1r = 11000

        # Min amplitude for KG1V
        self.min_amp_kg1v = 0.21

        # For detection of fringe jumps
        self.min_fringe = 0.25
        self.min_vib = 24.0
        self.fringe = 0.5
        self.npoints_long_time = 20
        self.fringe_long_time = 0.8
        self.max_jumps = 400  # The maximum number of jumps the code will try to correct for any given channel

        # For filtering the signal with wavelets
        self.wv_family = 'db5'
        self.wv_ncoeff_ne = 100
        self.wv_ncoeff_vib = 300

        self.temp_node = "VC/E-AVV-TMP"
        self.geometry_filename = "kg1_chord_geom.txt"
        
        self.mode = "Automatic Corrections"

        # Read in constants from file
        logger.info("Parsing config file {}".format(config_name))
        config = configparser.ConfigParser()
        file_read = config.read(config_name)


        #read users
        self.readusers = self._get_node_channumber_dict(config,"readusers")
        self.writeusers = self._get_node_channumber_dict(config,"writeusers")

        #KG1 signal to be validated
        self.kg1v = self._get_node_channumber_dict(config,"kg1v")



        # Other diagnostics/PPFs
        self.kg4_far = self._get_node_channumber_dict(config, "kg4_far")
        self.kg4_ell = self._get_node_channumber_dict(config, "kg4_ell")
        self.kg4_xg_ell = self._get_node_channumber_dict(config, "kg4_xg_ell")
        self.kg4r =   self._get_node_channumber_dict(config, "kg4_lid")
        self.kg4_xg_elld = self._get_node_channumber_dict(config, "kg4_xg_elld")

        #kg1 real time

        self.kg1rt =  self._get_node_channumber_dict(config, "kg1rt")

        self.elms = self._get_node_channumber_dict(config, "elms")
        self.pellets = self._get_node_channumber_dict(config, "pellets")
        self.hrts = self._get_node_channumber_dict(config, "hrts")
        self.lidar = self._get_node_channumber_dict(config, "lidar")

        self.hrts_ppf = self._get_node_channumber_dict(config, "hrts_ppf")

        # kg1v PPFs

        self.kg1r_ppf_vib = self._get_node_channumber_dict(config, "kg1r_ppf_vib")
        self.kg1r_ppf_fj_dcn = self._get_node_channumber_dict(config, "kg1r_ppf_fj_dcn")
        self.kg1r_ppf_fj_met = self._get_node_channumber_dict(config, "kg1r_ppf_fj_met")
        self.kg1r_ppf_bp_dcn = self._get_node_channumber_dict(config, "kg1r_ppf_bp_dcn")
        self.kg1r_ppf_bp_met = self._get_node_channumber_dict(config, "kg1r_ppf_bp_met")
        self.kg1r_ppf_jxb = self._get_node_channumber_dict(config, "kg1r_ppf_jxb")
        self.kg1r_ppf_type = self._get_node_channumber_dict(config, "kg1r_ppf_type")

        # JPF or PPF nodes not stored by channel number
        self.magnetics = { "ip": config["magnetics"]["ip"] }
        self.magnetics["bt_coil_current_av"] = config["magnetics"]["bt_coil_current_av"]
        self.magnetics["eddy_current"] = config["magnetics"]["eddy_current"]

        self.nbi = self._get_node_channumber_dict(config, "nbi")

        # Disruption node name & time before and after disruption where data is not corrected
        self.disruption = config["disruption"]["1"]
        self.dis_window = float(config["disruption"]["window"])


        geometry = config["geometry"]
        self.temp_node = geometry.get("temp_jpf", self.temp_node)
        self.geometry_filename = geometry.get("geom_filename", self.geometry_filename)
        
        
        correction = config["mode"]
        self.mode = correction.get("mode", self.mode)
        #self.kg1v_mode = self._get_node_channumber_dict(config, "mode")
    # ------------------------
    def _get_node_channumber_dict(self, config, section):
        """
        From config class, read in appropriate section.
        Put resulting variables into a dictionary, key is an integer.

        :param config: Instance of ConfigParser (with file already read in)
        :param section: The section to read in
        :return: Dictionary where key is an int, value is a string
        """
        try:
            items = config.items(section)
            node_dict = {}
            for chan, node in items:
                node_dict[int(chan)] = node
            return node_dict
        except configparser.NoSectionError:
            return {}

    # ------------------------
    def get_phase_node_dcn(self, chan, sig_type):
        """
        Return the appropriate JPF node name for the DCN phase, given the signal type & channel number

        :param chan: Channel number
        :param sig_type: Signal type: kg1r, kg1c_ldraw, kg1c_ld, kg1c_ldcor or kg1v
        :return: JPF node name
        """
        try:
            if sig_type == "kg1r":
                return self.kg1r_phase_dcn[chan]
            elif sig_type == "kg1c_ldraw":
                return self.kg1c_phase_ldraw_dcn[chan]
            elif sig_type == "kg1c_ld":
                return self.kg1c_phase_ld_dcn[chan]
            elif sig_type == "kg1c_ldcor":
                return self.kg1c_phase_ldcor_dcn[chan]
            elif sig_type == "kg1v":
                return self.kg1v_phase_dcn[chan]
            else:
                return ""
        except KeyError:
            return ""

    # ------------------------
    def get_phase_node_met(self, chan, sig_type):
        """
        Return the appropriate JPF node name for the MET phase, given the signal type & channel number

        :param chan: Channel number
        :param sig_type: Signal type: kg1r, kg1c_ldraw, kg1c_ld, kg1c_ldcor or kg1v
        :return: JPF node name
        """
        try:
            if sig_type == "kg1r":
                return self.kg1r_phase_met[chan]
            elif sig_type == "kg1c_ldraw":
                return self.kg1c_phase_ldraw_met[chan]
            elif sig_type == "kg1c_ld":
                return self.kg1c_phase_ld_met[chan]
            elif sig_type == "kg1c_ldcor":
                return self.kg1c_phase_ldcor_met[chan]
            elif sig_type == "kg1v":
                return self.kg1v_phase_met[chan]
            else:
                return ""
        except KeyError:
            return ""

    # ------------------------
    def get_amp_node_dcn(self, chan, sig_type):
        """
        Return the appropriate JPF node name for the DCN amplitude signal, given the signal type & channel number

        :param chan: Channel number
        :param sig_type: Signal type: kg1r, kg1c_ldraw, kg1c_ld, kg1c_ldcor or kg1v
        :return: JPF node name
        """
        try:
            if sig_type == "kg1r":
                return self.kg1r_amp_dcn[chan]
            elif (sig_type == "kg1c_ldraw"
                  or sig_type == "kg1c_ld"
                  or sig_type == "kg1c_ldcor"):
                return self.kg1c_cprb_dcn[chan]
            elif sig_type == "kg1v":
                return self.kg1v_amp_dcn[chan]
            else:
                return ""
        except KeyError:
            return ""

    # ------------------------
    def get_amp_node_met(self, chan, sig_type):
        """
        Return the appropriate JPF node name for the MET amplitude signal, given the signal type & channel number

        :param chan: Channel number
        :param sig_type: Signal type: kg1r, kg1c_ldraw, kg1c_ld, kg1c_ldcor or kg1v
        :return: JPF node name
        """
        try:
            if sig_type == "kg1r":
                return self.kg1r_amp_met[chan]
            elif (sig_type == "kg1c_ldraw"
                  or sig_type == "kg1c_ld"
                  or sig_type == "kg1c_ldcor"):
                return self.kg1c_cprb_met[chan]
            elif sig_type == "kg1v":
                return self.kg1v_amp_met[chan]
            else:
                return ""
        except KeyError:
            return ""

    # ------------------------
    def get_sts_node_dcn(self, chan, sig_type):
        """
        Return the appropriate JPF node name for the DCN KG1C STS signal, given the signal type & channel number

        :param chan: Channel number
        :param sig_type: Signal type: kg1c_ldraw, kg1c_ld or kg1c_ldcor
        :return: JPF node name
        """
        try:
            if (sig_type == "kg1c_ldraw"
                  or sig_type == "kg1c_ld"
                  or sig_type == "kg1c_ldcor"):
                return self.kg1c_sts_dcn[chan]
            else:
                return ""
        except KeyError:
            return ""

    # ------------------------
    def get_sts_node_met(self, chan, sig_type):
        """
        Return the appropriate JPF node name for the MET KG1C STS signal, given the signal type & channel number

        :param chan: Channel number
        :param sig_type: Signal type: kg1c_ldraw, kg1c_ld or kg1c_ldcor
        :return: JPF node name
        """
        try:
            if (sig_type == "kg1c_ldraw"
                  or sig_type == "kg1c_ld"
                  or sig_type == "kg1c_ldcor"):
                return self.kg1c_sts_met[chan]
            else:
                return ""
        except KeyError:
            return ""

    # ------------------------
    def get_fj_node_dcn(self, chan, sig_type):
        """
        Return the appropriate JPF node name for the DCN KG1C FJ signal, given the signal type & channel number

        :param chan: Channel number
        :param sig_type: Signal type: kg1c_ldraw, kg1c_ld or kg1c_ldcor
        :return: JPF node name
        """
        try:
            if (sig_type == "kg1c_ldraw"
                  or sig_type == "kg1c_ld"
                  or sig_type == "kg1c_ldcor"):
                return self.kg1c_fj_dcn[chan]
            else:
                return ""
        except KeyError:
            return ""

    # ------------------------
    def get_fj_node_met(self, chan, sig_type):
        """
        Return the appropriate JPF node name for the MET KG1C FJ signal, given the signal type & channel number

        :param chan: Channel number
        :param sig_type: Signal type: kg1c_ldraw, kg1c_ld or kg1c_ldcor
        :return: JPF node name
        """
        try:
            if (sig_type == "kg1c_ldraw"
                  or sig_type == "kg1c_ld"
                  or sig_type == "kg1c_ldcor"):
                return self.kg1c_fj_met[chan]
            else:
                return ""
        except KeyError:
            return ""

    # ------------------------
    def set_time_windows(self, ip_times, nbi_times, flattop_times):
        """
        Set time windows

        :param ip_times: [start ip, end ip]
        :param nbi_times: [start_nbi, end_nbi]
        :param flattop_times: [start_flat, end_flat]
        """
        self.time_ip["start_ip"] = ip_times[0]
        self.time_ip["end_ip"] = ip_times[1]
        self.time_ip["start_topip"] = flattop_times[0]
        self.time_ip["end_topip"] = flattop_times[1]
        self.time_ip["start_nbi"] = nbi_times[0]
        self.time_ip["end_nbi"] = nbi_times[1]
