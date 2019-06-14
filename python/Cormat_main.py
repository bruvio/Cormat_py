#!/usr/bin/env python
"""
Class that runs CORMAT_py GUI
"""


# ----------------------------
__author__ = "Bruno Viola"
__Name__ = "CORMAT_py"
__version__ = "0.15"
__release__ = "0"
__maintainer__ = "Bruno Viola"
__email__ = "bruno.viola@ukaea.uk"
__status__ = "Testing"
# __status__ = "Production"


import argparse
import logging
from types import SimpleNamespace
from logging.handlers import RotatingFileHandler
from logging import handlers
import os
import pathlib
# from pickle import dump,load
import pickle
import platform
import datetime
import sys
import time
from pathlib import Path
import CORMAT_GUI
import matplotlib.pyplot as plt
from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from areyousure_gui import Ui_areyousure_window
from accept_suggestion import Ui_suggestion_window
from consts import Consts
from elms_data import ElmsData
from find_disruption import find_disruption
from hrts_data import HRTSData
from kg1_ppf_data import Kg1PPFData
from kg4_data import Kg4Data
from library import * #containing useful function
from lidar_data import LIDARData
from mag_data import MagData
from matplotlib import gridspec
from matplotlib.backends.backend_qt4agg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import AutoMinorLocator
from nbi_data import NBIData
from pellet_data import PelletData
from ppf import *
from ppf_write import *
from signal_base import SignalBase
from custom_formatters import MyFormatter,QPlainTextEditLogger,HTMLFormatter
from support_classes import LineEdit,Key,KeyBoard,MyLocator
import inspect
import fileinput
import cProfile, pstats, io
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
import inspect



qm = QtGui.QMessageBox
qm_permanent = QtGui.QMessageBox
plt.rcParams["savefig.directory"] = os.chdir(os.getcwd())
myself = lambda: inspect.stack()[1][3]
logger = logging.getLogger(__name__)
# noinspection PyUnusedLocal
class CORMAT_GUI(QtGui.QMainWindow, CORMAT_GUI.Ui_CORMAT_py,
                 QPlainTextEditLogger):
    """

    Main control function for CORMATpy GUI.



    """

    def _initialize_widget(self, widget):
        """
        function that:
         - initialises every tab (widget)
         - add layout
         - add navigation toolbar and position it at the bottom of the tab
        :param widget: tab to initialise
        :return:
        """



        widget.setLayout(QtGui.QVBoxLayout())
        widget.layout().setContentsMargins(0, 710, 50,
                                           -0)  # (left, top, right, bottom)
        widget.layout().setSpacing(0)
        toolbar = NavigationToolbar(widget, self)
        widget.layout().addWidget(toolbar)
        # widget.figure.clear()
        # widget.draw()

    # ----------------------------
    def __init__(self, parent=None):
        """
        Setup the GUI, and connect the buttons to functions.

        Initialise widgets and canvas.
        Define defaults
        
        Moreover it checks if there is data in workspace and load it if pulse number is correct.
        
        


        """
        try:

            super(CORMAT_GUI, self).__init__(parent)
            self.setupUi(self)

            self.data = SimpleNamespace() # dictionary object that contains all data

            # -------------------------------
            # check if kg1 is stored in workspace
            # -------------------------------
            exists = os.path.isfile('./scratch/kg1_data.pkl')

            if exists :
                        logging.getLogger().disabled = True

                        self.load_pickle()

                        # logging.disable(logging.NOTSET)
                        logging.getLogger().disabled = False
                        logger.log(5,'checking pulse data in workspace')
                        list_attr=['self.data.KG1_data','self.data.KG4_data', 'self.data.MAG_data', 'self.data.PELLETS_data','self.data.ELM_data', 'self.data.HRTS_data','self.data.NBI_data', 'self.data.is_dis', 'self.data.dis_time','self.data.LIDAR_data']
                        for attr in list_attr:
                            # pyqt_set_trace()
                            if hasattr(self, attr):
                                delattr(self,attr)
                        self.setWindowTitle("CORMAT_py - {}".format(self.data.pulse))
                        self.lineEdit_jpn.setText(str(self.data.pulse))


                        del  self.data.pulse

            # -------------------------------
            # backup for kg1 data
            self.data.kg1_original = {}
            # -------------------------------
            # store normalised kg1?
            self.data.kg1_norm = {}
            # ----------------------
            # initialise data
            self.data.KG1_data = {}
            self.data.KG4_data = {}
            self.data.MAG_data = {}
            self.data.PELLETS_data = {}
            self.data.ELM_data = {}
            self.data.HRTS_data = {}
            self.data.NBI_data = {}
            self.data.is_dis = {}
            self.data.dis_time = {}
            self.data.LIDAR_data = {}

            #list where storing data point selected by user clicking on canvas
            self.data.coord_ch1 = []
            self.data.coord_ch2 = []
            self.data.coord_ch3 = []
            self.data.coord_ch4 = []
            self.data.coord_ch5 = []
            self.data.coord_ch6 = []
            self.data.coord_ch7 = []
            self.data.coord_ch8 = []




            ####
            self.totalcorrections_den =np.empty([7])
            self.totalcorrections_vib =np.empty([7])

            # storing backup of data when zeroing
            self.data.zeroingbackup_den = [ [],[],[],[],[],[],[],[]]
            self.data.zeroingbackup_vib = [ [],[],[],[],[],[],[],[]]
            # self.data.zeroingbackup_vib = []

            #setting zeroed vertical line to 100s
            # self.data.xzero_tail = 100
            # self.data.zeroing_start[self.chan] = 1e6 # index of starting of zeroing when zeroing tail data

            #
            # self.data.z = 1e6 #index of start of zeroing interval
            # self.data.zeroing_stop = 0 # index of end of zeroing interval
            #
            self.data.zeroed = np.zeros(8, dtype=bool) # array that stores info is channel has been tail zeroed
            self.data.zeroing_start =np.full(8,1e6, dtype=int)
            self.data.zeroing_stop = np.full(8,0, dtype=int)
            #
            # self.data.zeroing_start_min = 1e6 # minimum index of zeroing interval (to be shown in other channels)
            # self.data.zeroing_stop_max = 0# maximum index of zeroing interval (to be shown in other channels)
        #



            # -------------------------------
            #old pulse contains information on the last pulse analysed
            self.data.old_pulse = None
            #pulse is the current pulse
            self.data.pulse = None
            # -------------------------------
            # initialisation of control variables
            # -------------------------------
            # set saved status to False

            self.data.saved = False
            self.data.data_changed = False
            self.data.statusflag_changed = False

            logger.log(5,
                       "{} - saved is {} - data changed is {} - status flags changed is {}".format(
                           myself(), self.data.saved, self.data.data_changed,
                           self.data.statusflag_changed))

            # -------------------------------
            ###setting up the logger to write inside a Text box in the GUI
            # -------------------------------
            logTextBox = QPlainTextEditLogger(self)
            # You can format what is printed to text box
            #logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

            #logTextBox.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
            logTextBox.setFormatter(HTMLFormatter())
            logging.getLogger().addHandler(logTextBox)
            # You can control the logging level
            # logging.getLogger().setLevel(logger.info)

            # -------------------------------
            # initialising new pulse checkbox to false
            # -------------------------------
            self.checkBox_newpulse.setChecked(False)




            # -------------------------------
            # initialising tabs
            # -------------------------------
            self._initialize_widget(self.widget_LID1)
            self._initialize_widget(self.widget_LID2)
            self._initialize_widget(self.widget_LID3)
            self._initialize_widget(self.widget_LID4)
            self._initialize_widget(self.widget_LID5)
            self._initialize_widget(self.widget_LID6)
            self._initialize_widget(self.widget_LID7)
            self._initialize_widget(self.widget_LID8)
            self._initialize_widget(self.widget_LID_14)
            self._initialize_widget(self.widget_LID_58)
            self._initialize_widget(self.widget_LID_ALL)
            self._initialize_widget(self.widget_MIR)

            # set tabwidget index to 0 - lid1 is the tab shown at startup
            # self.tabWidget.setCurrentWidget(self.tabWidget.findChild(tabWidget, 'tab_LID1'))
            self.tabWidget.setCurrentIndex(0)
            # -------------------------------
            # initialising folders
            # -------------------------------
            logger.info('\tStart CORMATpy')
            logger.info('\t {}'.format(datetime.datetime.today().strftime('%Y-%m-%d')))
            cwd = os.getcwd()
            self.workfold = cwd
            self.home = cwd
            parent = Path(self.home)
            if "USR" in os.environ:
                logger.log(5, 'USR in env')
                # self.owner = os.getenv('USR')
                self.owner = os.getlogin()
            else:
                logger.log(5, 'using getuser to authenticate')
                import getpass
                self.owner = getpass.getuser()
            logger.log(5, 'this is your username {}'.format(self.owner))
            self.homefold = os.path.join(os.sep, 'u', self.owner)
            logger.log(5, 'this is your homefold {}'.format(self.homefold))
            home = str(Path.home())
            self.chain1 = '/common/chain1/kg1/'
            extract_history(
                self.workfold + '/run_out.txt',
                self.chain1 + 'cormat_out.txt')
            logger.info('copying to local user profile')
            logger.log(5, 'we are in %s', cwd)

            # -------------------------------
            # Read  config self.data.
            # -------------------------------
            logger.info(" Reading in constants.")
            # test_logger()
            # raise SystemExit


            try:
                self.data.constants = Consts("consts.ini", __version__)
                # constants = Kg1Consts("kg1_consts.ini", __version__)
            except KeyError:
                logger.error(" Could not read in configuration file consts.ini")
                sys.exit(65)

            self.data.poss_ne_corr = np.array([self.data.constants.CORR_NE]*10) * np.array([np.arange(10)+1]*len(self.data.constants.CORR_NE)).transpose()
            self.data.poss_vib_corr = np.array([self.data.constants.CORR_VIB]*10) * np.array([np.arange(10)+1]*len(self.data.constants.CORR_VIB)).transpose()
            self.data.poss_dcn_corr = np.array([self.data.constants.FJ_DCN]*10) * np.array([np.arange(10)+1]*len(self.data.constants.FJ_DCN)).transpose()
            self.data.poss_met_corr = np.array([self.data.constants.FJ_MET]*10) * np.array([np.arange(10)+1]*len(self.data.constants.FJ_MET)).transpose()

            # matrix for converting DCN & MET signals into density & mirror movement
            self.data.matrix_lat_channels = np.array([[self.data.constants.MAT11 , self.data.constants.MAT12 ],[self.data.constants.MAT21 , self.data.constants.MAT22 ]])
            self.data.Minv= np.linalg.inv(self.data.matrix_lat_channels)  # invert correction matrix for lateral channels


            self.data.sign_vib_corr = np.array(np.zeros(self.data.poss_vib_corr.shape) + 1)
            self.data.sign_vib_corr[np.where(self.data.poss_vib_corr < 0.0)] = -1

            # -------------------------------
            # list of authorized user to write KG1 ppfs
            # -------------------------------
            read_uis = []
            for user in self.data.constants.readusers.keys():
                user_name = self.data.constants.readusers[user]
                read_uis.append(user_name)
            self.exit_button.clicked.connect(self.handle_exit_button)
            self.PathTranfile = None
            self.PathCatalog = '/home'
            # -------------------------------
            # list of option to write ppf for current user
            # -------------------------------
            write_uis = []
            # -------------------------------
            # check if owner is in list of authorised users
            # -------------------------------
            if self.owner in read_uis:
                logger.info(
                    'user {} authorised to write public PPF'.format(self.owner))
                write_uis.insert(0, 'JETPPF')  # jetppf first in the combobox list
                write_uis.append(self.owner)
                # users.append('chain1')
            else:
                logger.info(
                    'user {} NOT authorised to write public PPF'.format(self.owner))
                write_uis.append(self.owner)
            # -------------------------------
            # initialise combobox
            self.comboBox_readuid.addItems(read_uis)
            self.comboBox_writeuid.addItems(write_uis)
            # -------------------------------
            # set combobox index to 1 so that the default write_uid is owner
            if len(write_uis) == 2:
                self.comboBox_writeuid.setCurrentIndex(1)
            else:
                self.comboBox_writeuid.setCurrentIndex(0)

            # -------------------------------
            # set default pulse
            # initpulse = pdmsht()
            #initpulse = 92121
            #self.lineEdit_jpn.setText(str(initpulse))
            # -------------------------------
            # -------------------------------
            # list of the second trace signal use to be compared with KG1
            # -------------------------------
            othersignallist = ['None', 'HRTS', 'Lidar', 'BremS', 'Far', 'CM',
                               'KG1_RT','LID1','LID2','LID3','LID4','LID5','LID6','LID7','LID8']

            self.comboBox_2ndtrace.addItems(othersignallist)
            self.comboBox_2ndtrace.activated[str].connect(self.plot_2nd_trace)
            # -------------------------------
            # list of markers
            # -------------------------------
            markers = ['None', 'ELMs', 'NBI', 'PELLETs', 'MAGNETICs']
            self.comboBox_markers.addItems(markers)
            self.comboBox_markers.activated[str].connect(self.plot_markers)
            # -------------------------------
            # disabling marker and second trace combo boxes
            # -------------------------------
            self.comboBox_markers.setEnabled(False)
            self.comboBox_2ndtrace.setEnabled(False)
            # -------------------------------
            # connecting functions to buttons
            # -------------------------------
            self.button_read_pulse.clicked.connect(self.handle_readbutton_master)
            # self.button_read_pulse.clicked.connect(self.handle_readbutton)
            self.button_saveppf.clicked.connect(self.handle_saveppfbutton)
            self.button_save.clicked.connect(self.dump_kg1)
            self.button_normalize.clicked.connect(self.handle_normalizebutton)
            self.button_restore.clicked.connect(self.handle_button_restore)
            # self.pushButton_apply.clicked.connect(self.handle_applybutton)
            self.pushButton_makeperm.clicked.connect(self.handle_makepermbutton)
            # self.pushButton_undo.clicked.connect(self.handle_undobutton)
            self.checkSFbutton.clicked.connect(self.checkStatuFlags)
            self.actionHelp.triggered.connect(self.handle_help_menu)
            self.actionOpen_PDF_guide.triggered.connect(self.handle_pdf_open)
            # -------------------------------
            # initialising code folders
            # -------------------------------
            try:
                # figure folder
                pathlib.Path(cwd + os.sep + 'figures').mkdir(parents=True,
                                                             exist_ok=True)
                # scratch folder - where you keep unsaved unfinished data
                pathlib.Path(cwd + os.sep + 'scratch').mkdir(parents=True,
                                                             exist_ok=True)
                # save foldere - where you keep saved pulse data
                pathlib.Path(cwd + os.sep + 'saved').mkdir(parents=True,
                                                           exist_ok=True)
            except SystemExit:
                raise SystemExit('failed to initialise folders')
            # -------------------------------
            # disable many button to avoid conflicts at startup
            # -------------------------------
            self.button_saveppf.setEnabled(False)
            self.button_save.setEnabled(False)
            self.checkSFbutton.setEnabled(False)
            self.button_normalize.setEnabled(False)
            # self.pushButton_apply.setEnabled(False)
            self.pushButton_makeperm.setEnabled(False)
            self.pushButton_undo.setEnabled(False)
            self.button_restore.setEnabled(False)
            # -------------------------------
            # run code by default
            # self.button_read_pulse.click()
            # -------------------------------
            # -------------------------------
            # initialize to zero status flag radio buttons
            # -------------------------------
            self.radioButton_statusflag_0.setChecked(False)
            self.radioButton_statusflag_1.setChecked(False)
            self.radioButton_statusflag_2.setChecked(False)
            self.radioButton_statusflag_3.setChecked(False)
            self.radioButton_statusflag_4.setChecked(False)
            # -------------------------------
            # set status flag radio buttons to false
            self.groupBox_statusflag.setEnabled(False)
            # -------------------------------
            # -------------------------------
            # set read uid combo box to disabled
            self.comboBox_readuid.setEnabled(False)
            # -------------------------------
            # to disable a tab use
            # self.tabWidget.setTabEnabled(3, False)
            # -------------------------------
            # setup automatic check on status flag
            # -------------------------------
            self.checkBox_newpulse.toggled.connect(
                lambda: self.handle_check_status(self.checkBox_newpulse))
            # -------------------------------
            # #disable tab as there is nothing plotted
            self.tabWidget.setTabEnabled(0, False)
            self.tabWidget.setTabEnabled(1, False)
            self.tabWidget.setTabEnabled(2, False)
            self.tabWidget.setTabEnabled(3, False)
            self.tabWidget.setTabEnabled(4, False)
            self.tabWidget.setTabEnabled(5, False)
            self.tabWidget.setTabEnabled(6, False)
            self.tabWidget.setTabEnabled(7, False)
            self.tabWidget.setTabEnabled(8, False)
            self.tabWidget.setTabEnabled(9, False)
            self.tabWidget.setTabEnabled(10, False)
            self.tabWidget.setTabEnabled(11, False)
            # -------------------------------
            # making documentation
            # -------------------------------
            if (args.documentation).lower() == 'yes':
                logger.info('creating documentation')
                os.chdir('../docs')
                import subprocess
                subprocess.check_output('make html', shell=True)
                subprocess.check_output('make latex', shell=True)
                os.chdir(self.home)

            #adding personalized object LineEdit to widget in GUI
            self.lineEdit_mancorr = LineEdit()
            self.kb = KeyBoard(self.lineEdit_mancorr)
            self.gridLayout_21.addWidget(self.lineEdit_mancorr, 3, 0, 1, 2)




            # -------------------------------








            
            logger.info('INIT DONE')
            #auto click read button
            # self.button_read_pulse.click()
        except:
            logger.error('Error!')



    #-------------------------------
    @QtCore.pyqtSlot()
    def handle_readbutton_master(self):
        """
        implemets what happen when clicking the load button on the GUI
        the logic is explained in the FLowDiagram ../FlowDiagram/load_button_new.dia
        """

        # -------------------------------
        # reading pulse from GUI
        # -------------------------------
        self.data.pulse = self.lineEdit_jpn.text()


        if self.data.pulse is '': #user has not entered a pulse number
            logger.error('PLEASE USE JPN lower than {}'.format((pdmsht())))
            assert self.data.pulse is not '', "ERROR no pulse selected"
            return


        else:
            #self.data.pulse = int(self.lineEdit_jpn.text())
            try:
                int(self.data.pulse)

            except ValueError:
                logger.error('PLEASE USE JPN lower than {}'.format((pdmsht())))
                return

            if int(self.data.pulse) <= pdmsht():
                   pass # user has entered a valid pulse number
            else:
                logger.error('PLEASE USE JPN lower than {}'.format((pdmsht())))
                return



        self.data.pulse = int(self.lineEdit_jpn.text())
        logger.log(5, "resetting Canvas before reading data")
        # status flag groupbox is disabled
        self.groupBox_statusflag.setEnabled(False)
        self.tabWidget.setCurrentIndex(0)

        # disable "normalize" and "restore" buttons
        self.button_normalize.setEnabled(False)
        self.button_restore.setEnabled(False)
        self.comboBox_markers.setEnabled(False)
        self.comboBox_2ndtrace.setEnabled(False)
        self.comboBox_2ndtrace.setCurrentIndex(0)
        self.comboBox_markers.setCurrentIndex(0)



        self.widget_LID1.figure.clear()
        self.widget_LID1.draw()

        self.widget_LID2.figure.clear()
        self.widget_LID2.draw()

        self.widget_LID3.figure.clear()
        self.widget_LID3.draw()

        self.widget_LID4.figure.clear()
        self.widget_LID4.draw()

        self.widget_LID5.figure.clear()
        self.widget_LID5.draw()

        self.widget_LID6.figure.clear()
        self.widget_LID6.draw()

        self.widget_LID7.figure.clear()
        self.widget_LID7.draw()

        self.widget_LID8.figure.clear()
        self.widget_LID8.draw()

        self.widget_LID_14.figure.clear()
        self.widget_LID_14.draw()

        self.widget_LID_58.figure.clear()
        self.widget_LID_58.draw()

        self.widget_LID_ALL.figure.clear()
        self.widget_LID_ALL.draw()

        self.widget_MIR.figure.clear()
        self.widget_MIR.draw()

        #
        #


        # -------------------------------
        # check if kg1 is stored in workspace
        # -------------------------------
        exists = os.path.isfile('./scratch/kg1_data.pkl')

        if exists :
            assert(exists)
            logger.info( "The workspace contains data not saved to ppf")
            self.data.data_changed = True
            self.data.statusflag_changed = True
            self.data.saved = False

        else:
            pass



        # data_changed = equalsFile('./saved/' + str(self.data.pulse) + '_kg1.pkl',
        #                           './scratch/' + str(self.data.pulse) + '_kg1.pkl')

        if (self.data.data_changed | self.data.statusflag_changed) == True: # data has changed
            logger.log(5," data or status flags have changed")

            if self.data.saved:  # data saved to ppf
                logger.log(5, "  data or status flag have been saved to PPF")
                if (self.checkBox_newpulse.isChecked()):
                    logger.log(5, '{} is  checked'.format(self.checkBox_newpulse.objectName()))

                    # -------------------------------
                    # READ self.data.
                    # -------------------------------
                    self.data.zeroed = np.zeros(8,
                                                dtype=bool)  # array that stores info is channel has been tail zeroed
                    self.data.zeroing_start = np.full(8, 1e6, dtype=int)
                    self.data.zeroing_stop = np.full(8, 0, dtype=int)  #
                    self.data.zeroingbackup_den = [[], [], [], [], [], [], [],
                                                   []]
                    self.data.zeroingbackup_vib = [[], [], [], [], [], [], [],
                                                   []]


                    self.read_uid = str(self.comboBox_readuid.currentText())
                    logger.info("Reading data for pulse {}".format(str(self.data.pulse)))
                    logger.info('reading data with uid -  {}'.format((str(self.read_uid))))
                    success = self.readdata()
                    # self.tabWidget.setCurrentIndex(0)
                    # self.tabSelected(arg=0)
                    # -------------------------------
                    # PLOT KG1 self.data.
                    # -------------------------------
                    if success:
                        self.plot_data()

                        # -------------------------------
                        # update GUI after plot
                        # -------------------------------

                        self.GUI_refresh()
                        self.setWindowTitle(
                            "CORMAT_py - {}".format(self.data.pulse))

                        self.data.old_pulse = self.data.pulse
                    else:
                        logger.error("ERROR reading data")


                else:
                    logging.warning(' NO action performed \t')
                    logging.warning('\t please click new pulse!')# new pulse not checked
                    pass

            else:  # pulse not saved to ppf
                logger.log(5, "data or status flag have NOT been saved to PPF")

                if (self.checkBox_newpulse.isChecked()):
                    assert ((self.data.data_changed | self.data.statusflag_changed) & (
                        not self.data.saved) & (
                                self.checkBox_newpulse.isChecked()))

                    logger.log(5, '{} is  checked'.format(self.checkBox_newpulse.objectName()))

                    # if exists and and new pulse checkbox is checked then ask for confirmation if user wants to carry on
                    #logger.info(' pulse data already downloaded - you are requesting to download again')
                    self.areyousure_window = QtGui.QMainWindow()
                    self.ui_areyousure = Ui_areyousure_window()
                    self.ui_areyousure.setupUi(self.areyousure_window)
                    self.areyousure_window.show()

                    self.ui_areyousure.pushButton_YES.clicked.connect(
                        self.handle_yes)
                    self.ui_areyousure.pushButton_NO.clicked.connect(
                        self.handle_no)
                else:
                    logger.log(5, '{} is NOT  checked'.format(self.checkBox_newpulse.objectName()))
                    # pyqt_set_trace()
                    # logging.disable(logger.info)
                    # logging.getLogger().disabled = True

                    self.load_pickle()

                    # logging.disable(logging.NOTSET)
                    # logging.getLogger().disabled = False
                    logger.log(5,'checking pulse data in workspace')
                    # pyqt_set_trace()

                    self.data.old_pulse = self.data.pulse

                    self.data.pulse = int(self.lineEdit_jpn.text())
                    # pyqt_set_trace()
                    list_attr=['self.data.KG1_data','self.data.KG4_data', 'self.data.MAG_data', 'self.data.PELLETS_data','self.data.ELM_data', 'self.data.HRTS_data','self.data.NBI_data', 'self.data.is_dis', 'self.data.dis_time','self.data.LIDAR_data']
                    for attr in list_attr:
                        # pyqt_set_trace()
                        if hasattr(self, attr):
                            delattr(self,attr)
                    # pyqt_set_trace()

                    # if (self.data.old_pulse is None) | (self.data.old_pulse == self.data.pulse):
                    if  (self.data.old_pulse == self.data.pulse):
                        # -------------------------------
                        # READ self.data.
                        # -------------------------------
                        self.read_uid = str(self.comboBox_readuid.currentText())
                        logger.info('reading data with uid -  {}'.format(
                                (str(self.read_uid))))
                        self.load_pickle()

                        for chan in self.data.KG1_data.density.keys():
                            logger.log(5, 'enabling channel {}'.format(chan))
                            self.tabWidget.setTabEnabled(chan - 1, True)

                        logger.log(5, 'enabling tab {}'.format(9))
                        self.tabWidget.setTabEnabled(8, True)
                        logger.log(5, 'enabling tab {}'.format(10))
                        self.tabWidget.setTabEnabled(9, True)
                        logger.log(5, 'enabling tab {}'.format(11))
                        self.tabWidget.setTabEnabled(10, True)
                        logger.log(5, 'enabling tab {}'.format(12))
                        self.tabWidget.setTabEnabled(11, True)
                        # self.tabWidget.setCurrentIndex(0)
                        # self.tabSelected(arg=0)
                        # -------------------------------
                        # PLOT KG1 self.data.
                        # -------------------------------

                        self.plot_data()

                            # -------------------------------
                            # update GUI after plot
                            # -------------------------------

                        self.GUI_refresh()
                        self.setWindowTitle(
                            "CORMAT_py - {}".format(self.data.pulse))
                        self.data.old_pulse = self.data.pulse



                    elif self.data.old_pulse != self.data.pulse:
                        logging.error('no action performed, check input data')
                        logging.error('old pulse is {} - selected pulse is {}'.format(str(self.data.old_pulse),str(self.data.pulse)))
                        logging.error('you have unsaved data in your workspace!')
                        pass
        else:
            if (self.checkBox_newpulse.isChecked()):
                logger.log(5, ' {} is  checked'.format(self.checkBox_newpulse.objectName()))
                # if exists and and new pulse checkbox is checked then ask for confirmation if user wants to carry on
                #logger.info(' pulse data already downloaded - you are requesting to download again')
                self.areyousure_window = QtGui.QMainWindow()
                self.ui_areyousure = Ui_areyousure_window()
                self.ui_areyousure.setupUi(self.areyousure_window)
                self.areyousure_window.show()

                self.ui_areyousure.pushButton_YES.clicked.connect(
                    self.handle_yes)
                self.ui_areyousure.pushButton_NO.clicked.connect(self.handle_no)
            else:
                logger.log(5, '{} is NOT checked'.format(self.checkBox_newpulse.objectName()))
                logging.error(' no action performed')



        #now set
        self.data.saved = False
        self.data.statusflag_changed = False
        self.data.data_changed = False
        logger.log(5, " {} - saved is {} - data changed is {} - status flags changed is {}".format(myself(),self.data.saved,self.data.data_changed, self.data.statusflag_changed))


        # pyqt_set_trace()


# ----------------------------


# -------------------------
    @QtCore.pyqtSlot()
    def checkStatuFlags(self):
        """
        reads the list containing pulse status flag
        :return:
        """

        self.data.SF_list = [int(self.data.SF_ch1),
                        int(self.data.SF_ch2),
                        int(self.data.SF_ch3),
                        int(self.data.SF_ch4),
                        int(self.data.SF_ch5),
                        int(self.data.SF_ch6),
                        int(self.data.SF_ch7),
                        int(self.data.SF_ch8)]

        logger.info('%s has the following SF %s', str(self.data.pulse),
                     self.data.SF_list)

# ------------------------



# ------------------------
    def canvasselected(self, arg=None):
        """
        function that convert arg number into tab name
        it also sets the SF value when changing tabs
        :param arg: index of canvas
        :return:
        """

        # logger.log(5, 'tab number is {}'.format(str(arg + 1)))
        if arg == 0:
            logger.log(5, 'status flag is {}'.format(str(self.data.SF_ch1)))
            self.groupBox_statusflag.setEnabled(True)
            self.current_tab = 'LID_1'
            self.chan = '1'
            self.set_status_flag_radio(int(self.data.SF_ch1))
        if arg == 1:
            logger.log(5, 'status flag is {}'.format(str(self.data.SF_ch2)))
            self.groupBox_statusflag.setEnabled(True)
            self.current_tab = 'LID_2'
            self.chan = '2'
            self.set_status_flag_radio(int(self.data.SF_ch2))

        if arg == 2:
            logger.log(5, 'status flag is {}'.format(str(self.data.SF_ch3)))
            self.groupBox_statusflag.setEnabled(True)
            self.current_tab = 'LID_3'
            self.chan = '3'
            self.set_status_flag_radio(int(self.data.SF_ch3))

        if arg == 3:
            logger.log(5, 'status flag is {}'.format(str(self.data.SF_ch4)))
            self.groupBox_statusflag.setEnabled(True)
            self.current_tab = 'LID_4'
            self.chan = '4'
            self.set_status_flag_radio(int(self.data.SF_ch4))

        if arg == 4:
            logger.log(5, 'status flag is {}'.format(str(self.data.SF_ch5)))
            self.groupBox_statusflag.setEnabled(True)
            self.current_tab = 'LID_5'
            self.chan = '5'
            self.set_status_flag_radio(int(self.data.SF_ch5))

        if arg == 5:
            logger.log(5, 'status flag is {}'.format(str(self.data.SF_ch6)))
            self.groupBox_statusflag.setEnabled(True)
            self.current_tab = 'LID_6'
            self.chan = '6'
            self.set_status_flag_radio(int(self.data.SF_ch6))

        if arg == 6:
            logger.log(5, 'status flag is {}'.format(str(self.data.SF_ch7)))
            self.groupBox_statusflag.setEnabled(True)
            self.current_tab = 'LID_7'
            self.chan = '7'
            self.set_status_flag_radio(int(self.data.SF_ch7))

        if arg == 7:
            logger.log(5, 'status flag is {}'.format(str(self.data.SF_ch8)))
            self.groupBox_statusflag.setEnabled(True)
            self.current_tab = 'LID_8'
            self.chan = '8'
            self.set_status_flag_radio(int(self.data.SF_ch8))
        if arg == 8:
            self.groupBox_statusflag.setEnabled(False)
            self.current_tab = 'LID_1-4'
            self.chan = 'vertical'
        if arg == 9:
            self.groupBox_statusflag.setEnabled(False)
            self.current_tab = 'LID_5-8'
            self.chan = 'lateral'
        if arg == 10:
            self.groupBox_statusflag.setEnabled(False)
            self.current_tab = 'LID_ALL'
            self.chan = 'all'
        if arg == 11:
            self.groupBox_statusflag.setEnabled(False)
            self.current_tab = 'MIR'
            self.chan = 'vib'
        self.gettotalcorrections()
        logger.log(5, '\t: current Tab is {}'.format(self.current_tab))
#-------------------------
    def setcoord(self,chan,reset=False):
        """
        connects selected tab to its own list of selected data points

        :param reset:
        :return:
        """
        if reset is False:
            if str(chan) == '1':
                logger.log(5, 'no reset, coord_ch1 '.format(self.data.coord_ch1))
                return self.data.coord_ch1
            elif str(self.chan) == '2':
                logger.log(5,
                           'no reset, coord_ch1 '.format(self.data.coord_ch2))
                return self.data.coord_ch2
            elif str(self.chan) == '3':
                logger.log(5,
                           'no reset, coord_ch1 '.format(self.data.coord_ch3))
                return self.data.coord_ch3
            elif str(self.chan) == '4':
                logger.log(5,
                           'no reset, coord_ch1 '.format(self.data.coord_ch4))
                return self.data.coord_ch4
            elif str(self.chan) == '5':
                logger.log(5,
                           'no reset, coord_ch1 '.format(self.data.coord_ch5))
                return self.data.coord_ch5
            elif str(self.chan) == '6':
                logger.log(5,
                           'no reset, coord_ch1 '.format(self.data.coord_ch6))
                return self.data.coord_ch6
            elif str(self.chan) == '7':
                logger.log(5,
                           'no reset, coord_ch1 '.format(self.data.coord_ch7))
                return self.data.coord_ch7
            elif str(self.chan) == '8':
                logger.log(5,
                           'no reset, coord_ch1 '.format(self.data.coord_ch8))
                return self.data.coord_ch8
        elif reset is True and chan =='all':
            #reset all channels
            logger.log(5, 'reset all ')
            self.data.coord_ch1 = []
            self.data.coord_ch2 = []
            self.data.coord_ch3 = []
            self.data.coord_ch4 = []
            self.data.coord_ch5 = []
            self.data.coord_ch6 = []
            self.data.coord_ch7 = []
            self.data.coord_ch8 = []


        elif reset is True:
            #reset single channel
            if str(chan) == '1':
                logger.log(5, ' reset coord_ch1 ')
                self.data.coord_ch1 = []
            elif str(chan) == '2':
                logger.log(5, ' reset coord_ch2 ')
                self.data.coord_ch2 = []
            elif str(chan) == '3':
                logger.log(5, ' reset coord_ch3 ')
                self.data.coord_ch3 = []
            elif str(chan) == '4':
                logger.log(5, ' reset coord_ch4 ')
                self.data.coord_ch4 = []
            elif str(chan) == '5':
                logger.log(5, ' reset coord_ch5 ')
                self.data.coord_ch5 = []
            elif str(chan) == '6':
                logger.log(5, ' reset coord_ch6 ')
                self.data.coord_ch6 = []
            elif str(chan) == '7':
                logger.log(5, ' reset coord_ch7 ')
                self.data.coord_ch7 = []
            elif str(chan) == '8':
                logger.log(5, ' reset coord_ch8 ')
                self.data.coord_ch8 = []



# -------------------------
    def checkstate(self, button):

        """
        connect tab number to LID channel and sets status flag
        it also performs a check if the user clicked a radio button to change status flag for current tab/channel
        :param button:
        :return:
        """
        # snd = self.sender() # gets object that called


        SF = int(button.objectName().split('_')[2])  # statusflag value selected



        if self.current_tab == 'LID_1':
            self.data.SF_ch1 = SF
        if self.current_tab == 'LID_2':
            self.data.SF_ch2 = SF
        if self.current_tab == 'LID_3':
            self.data.SF_ch3 = SF
        if self.current_tab == 'LID_4':
            self.data.SF_ch4 = SF
        if self.current_tab == 'LID_5':
            self.data.SF_ch5 = SF
        if self.current_tab == 'LID_6':
            self.data.SF_ch6 = SF
        if self.current_tab == 'LID_7':
            self.data.SF_ch7 = SF
        if self.current_tab == 'LID_8':
            self.data.SF_ch8 = SF


        if (self.current_tab == 'LID_1') & (int(self.data.SF_old1) != int(self.data.SF_ch1)):

            self.data.statusflag_changed = True
            logger.log(5, "status flag LID1 changed by user")

        elif (self.current_tab == 'LID_2') & (int(self.data.SF_old2) != int(self.data.SF_ch2)):

            self.data.statusflag_changed = True
            logger.log(5, "status flag LID2 changed by user")

        elif (self.current_tab == 'LID_3') &  (int(self.data.SF_old3) != int(self.data.SF_ch3)):

            self.data.statusflag_changed = True
            logger.log(5, "status flag LID3 changed by user")

        elif (self.current_tab == 'LID_4') & (int(self.data.SF_old4) != int(self.data.SF_ch4)):

            self.data.statusflag_changed = True
            logger.log(5, "status flag LID4 changed by user")

        elif (self.current_tab == 'LID_5') & (int(self.data.SF_old5) != int(self.data.SF_ch5)):

            self.data.statusflag_changed = True
            logger.log(5, "status flag LID5 changed by user")

        elif (self.current_tab == 'LID_6') & (int(self.data.SF_old6) != int(self.data.SF_ch6)):

            self.data.statusflag_changed = True
            logger.log(5, "status flag LID6 changed by user")

        elif (self.current_tab == 'LID_7') & (int(self.data.SF_old7) != int(self.data.SF_ch7)):

            self.data.statusflag_changed = True
            logger.log(5, "status flag LID7 changed by user")

        elif (self.current_tab == 'LID_8') & (int(self.data.SF_old8) != int(self.data.SF_ch8)):

            self.data.statusflag_changed = True
            logger.log(5, "status flag LID8 changed by user")


# -------------------------

    def set_status_flag_radio(self, value):
        """
        converts status flag integer value into boolean to check SF radio buttons in GUI
        :param value: status flag to be applied to selected channel
        :return:
        """
        if value == 0:
            self.radioButton_statusflag_0.setChecked(True)
            self.radioButton_statusflag_1.setChecked(False)
            self.radioButton_statusflag_2.setChecked(False)
            self.radioButton_statusflag_3.setChecked(False)
            self.radioButton_statusflag_4.setChecked(False)
        if value == 1:
            self.radioButton_statusflag_0.setChecked(False)
            self.radioButton_statusflag_1.setChecked(True)
            self.radioButton_statusflag_2.setChecked(False)
            self.radioButton_statusflag_3.setChecked(False)
            self.radioButton_statusflag_4.setChecked(False)
        if value == 2:
            self.radioButton_statusflag_0.setChecked(False)
            self.radioButton_statusflag_1.setChecked(False)
            self.radioButton_statusflag_2.setChecked(True)
            self.radioButton_statusflag_3.setChecked(False)
            self.radioButton_statusflag_4.setChecked(False)
        if value == 3:
            self.radioButton_statusflag_0.setChecked(False)
            self.radioButton_statusflag_1.setChecked(False)
            self.radioButton_statusflag_2.setChecked(False)
            self.radioButton_statusflag_3.setChecked(True)
            self.radioButton_statusflag_4.setChecked(False)
        if value == 4:
            self.radioButton_statusflag_0.setChecked(False)
            self.radioButton_statusflag_1.setChecked(False)
            self.radioButton_statusflag_2.setChecked(False)
            self.radioButton_statusflag_3.setChecked(False)
            self.radioButton_statusflag_4.setChecked(True)

        logger.log(5, 'data saved is {} - status flag saved is - data changed is {}'.format(self.data.saved,self.data.statusflag_changed, self.data.data_changed))


    def load_scratch(self):
        """
        reloads data dumped to scratch

        :return:
        """
        logger.debug(' loading pulse data')
        with open('./scratch/kg1_data.pkl',
                  'rb') as f:  # Python 3: open(..., 'rb')
            [self.data.KG1_data, self.data.SF_list, self.data.unval_seq, self.data.val_seq,
             self.read_uid] = pickle.load(f)
        f.close()
        logger.info(' workspace loaded')


    # ------------------------
    def load_pickle(self,kg1only=False):
        """
        loads last saved data from non saved operations
        data are saved in pickle format (binary)

        also to be used when reloading a pulse
        """
        if kg1only is False:

            logger.info(' loading pulse data from workspace')
            # Python 3: open(..., 'rb')
            with open('./saved/data.pkl',
                      'rb') as f:
                [self.data.pulse, self.data.KG1_data,
                 self.data.KG4_data, self.data.MAG_data, self.data.PELLETS_data,
                 self.data.ELM_data, self.data.HRTS_data,
                 self.data.NBI_data, self.data.is_dis, self.data.dis_time,
                 self.data.LIDAR_data,self.data.zeroing_start,self.data.zeroing_stop,self.data.zeroed, self.data.zeroingbackup_den,
                self.data.zeroingbackup_vib] = pickle.load(f)
            f.close()
            with open('./scratch/kg1_data.pkl',
                      'rb') as f:  # Python 3: open(..., 'rb')
                [self.data.KG1_data, self.data.SF_list, self.data.unval_seq, self.data.val_seq,
                 self.read_uid,self.data.zeroing_start,self.data.zeroing_stop, self.data.zeroingbackup_den,self.data.zeroingbackup_vib] = pickle.load(f)
            f.close()
            logger.info(' workspace loaded')
            logger.info(
                ' workspace data comes from userid {}'.format(self.read_uid))
            logger.info(
                '{} has the following SF {}'.format(str(self.data.pulse), self.data.SF_list))
            if self.data.KG1_data.mode != "Automatic Corrections":
                self.data.KG1_data.correctedby = self.data.KG1_data.mode.split(" ")[2]
                logger.info('{} last validated seq is {} by {}'.format(str(self.data.pulse),
                                                                        str(self.data.val_seq),self.data.KG1_data.correctedby))

            [self.data.SF_ch1,
             self.data.SF_ch2,
             self.data.SF_ch3,
             self.data.SF_ch4,
             self.data.SF_ch5,
             self.data.SF_ch6,
             self.data.SF_ch7,
             self.data.SF_ch8] = self.data.SF_list

            self.data.SF_old1 = self.data.SF_ch1
            self.data.SF_old2 = self.data.SF_ch2
            self.data.SF_old3 = self.data.SF_ch3
            self.data.SF_old4 = self.data.SF_ch4
            self.data.SF_old5 = self.data.SF_ch5
            self.data.SF_old6 = self.data.SF_ch6
            self.data.SF_old7 = self.data.SF_ch7
            self.data.SF_old8 = self.data.SF_ch8

            # set saved status to False
            self.data.saved = False
            self.data.data_changed = False
            self.data.statusflag_changed = False
            logger.log(5, "load_pickle - saved is {} - data changed is {} - status flags changed is {}".format(self.data.saved,self.data.data_changed, self.data.statusflag_changed))
        else:
            logger.log(5,'recovering KG1 data only')
            with open('./scratch/kg1_data.pkl',
                      'rb') as f:  # Python 3: open(..., 'rb')
                [dummy, _, _, _,
                 _] = pickle.load(f)
            self.data.KG1_data.fj_dcn = dummy.fj_dcn
            f.close()



    # ------------------------
    def save_to_pickle(self,folder):
        """
        saves to pickle experimental data
        :param folder: for now user can save either to saved or scratch folder
        :return:
        """
        logger.info(' saving pulse data to {}'.format(folder))
        with open('./' + folder + '/data.pkl', 'wb') as f:
            pickle.dump(
                [self.data.pulse, self.data.KG1_data,
                 self.data.KG4_data, self.data.MAG_data, self.data.PELLETS_data,
                 self.data.ELM_data, self.data.HRTS_data,
                 self.data.NBI_data, self.data.is_dis, self.data.dis_time,
                 self.data.LIDAR_data,self.data.zeroing_start,self.data.zeroing_stop,self.data.zeroed,self.data.zeroingbackup_den,self.data.zeroingbackup_vib], f)
        f.close()
        logger.info(' data saved to {}'.format(folder))

    # ------------------------
    def save_kg1(self,folder):
        """
        module that saves just kg1 data to folder
        :param folder:
        :return:
        """
        logger.debug(' saving KG1 data to {}'.format(folder))
        with open('./' + folder + '/kg1_data.pkl', 'wb') as f:
            pickle.dump(
                [self.data.KG1_data, self.data.SF_list, self.data.unval_seq, self.data.val_seq,
                 self.read_uid,self.data.zeroing_start,self.data.zeroing_stop, self.data.zeroingbackup_den,self.data.zeroingbackup_vib], f)
        f.close()
        logger.info(' KG1 data saved to {}'.format(folder))

#---------------------------------
    @QtCore.pyqtSlot()
    def dump_kg1(self):
        """
        temporary save kg1 data to scratch folder
        :return:
        """
        # logger.info(' dumping KG1 data')
        self.save_kg1('scratch')
        # logger.info(' KG1 data dumped to scratch')
        # if workspace is saved then delete data point collected (so no need to undo)
        self.setcoord(reset=True,chan='all')


#----------------------------

    @QtCore.pyqtSlot()
    def handle_no(self):
        """
        functions that ask to confirm if user wants NOT to proceed

        to set read data for selected pulse
    """

        # button_name = button.objectName()
        # print(button_name)


        logger.log(5, 'pressed %s button',
                      self.ui_areyousure.pushButton_NO.text())
        logger.info('go back and perform a different action')

        self.ui_areyousure.pushButton_NO.setChecked(False)

        self.areyousure_window.hide()

    # ----------------------------
    @QtCore.pyqtSlot()
    def handle_yes(self):
        """
        functions that ask to confirm if user wants to proceed

        to set read data for selected pulse
        """

        # button_name = button.text()
        # print(button_name)

        self.ui_areyousure.pushButton_YES.setChecked(False)

        self.areyousure_window.hide()


        logger.log(5, 'pressed %s button',
                      self.ui_areyousure.pushButton_YES.text())

        self.read_uid = self.comboBox_readuid.currentText()
        logger.info("Reading data for pulse {}".format(str(self.data.pulse)))
        success = self.readdata()

        if success:
            # status flag groupbox is disabled
            self.groupBox_statusflag.setEnabled(False)
            self.checkSFbutton.setEnabled(False)
            self.comboBox_markers.setEnabled(False)
            # disable "normalize" and "restore" buttons
            self.button_normalize.setEnabled(False)
            self.button_restore.setEnabled(False)
            self.comboBox_2ndtrace.setCurrentIndex(0)
            self.comboBox_markers.setCurrentIndex(0)


            self.plot_data()

            self.GUI_refresh()
            self.setWindowTitle("CORMAT_py - {}".format(self.data.pulse))
            self.data.old_pulse = self.data.pulse
            self.data.zeroed = np.zeros(8,
                                        dtype=bool)  # array that stores info is channel has been tail zeroed
            self.data.zeroing_start = np.full(8, 1e6, dtype=int)
            self.data.zeroing_stop = np.full(8, 0, dtype=int)  #

            self.data.zeroingbackup_den = [[], [], [], [], [], [], [], []]
            self.data.zeroingbackup_vib = [[], [], [], [], [], [], [], []]


            # now set
            logger.log(5, " {} - saved is {} - data changed is {} - status flags changed is {}".format(myself(),self.data.saved,self.data.data_changed, self.data.statusflag_changed))
        else:
            logger.error("ERROR reading data")

    # -----------------------

    def handle_yes_reload(self):
        """
        module that handles readloading already downloaded data
        :return:
        """

        logger.info(' pulse data already downloaded')
        self.load_pickle()

        # self.tabWidget.setCurrentIndex(0)
        # self.tabSelected(arg=0)

        # -------------------------------
        # PLOT KG1 self.data.
        # -------------------------------

        self.plot_data()

        # -------------------------------
        # update GUI after plot
        # -------------------------------

        self.GUI_refresh()
        #

        self.data.old_pulse = self.data.pulse
        logger.log(5, 'old pulse is {}, new pulse is {}'.format(self.data.old_pulse, self.data.pulse))
        # now set
        self.data.saved = False
        self.data.statusflag_changed = False
        self.data.data_changed = False
        self.gettotalcorrections()
        logger.log(5, 'data saved is {} - status flag saved is - data changed is {}'.format(self.data.saved,self.data.statusflag_changed, self.data.data_changed))
#-------------------------

# -------------------------------
    def readdata(self):

        """
        function that reads data as described in const.ini
        :return: True if success
                False if error
                saves data to pickle files: one just for KG1 (kg1_data) and one for everything else (data.pkl)
        """


        # -------------------------------
        # 1. Read in Magnetics data
        # -------------------------------
        logger.info("             Reading in magnetics data.")
        self.data.MAG_data = MagData(self.data.constants)
        success = self.data.MAG_data.read_data(self.data.pulse)
        if not success:
            logging.error(
                'no MAG data for pulse {} with uid {}'.format(self.data.pulse,
                                                               self.read_uid))


        # -------------------------------
        # 2. Read in KG1 data
        # -------------------------------
        logger.info("             Reading in KG1 data.")
        self.data.KG1_data = Kg1PPFData(self.data.constants,self.data.pulse)


        self.read_uid = self.comboBox_readuid.currentText()
        success = self.data.KG1_data.read_data(self.data.pulse, read_uid=self.read_uid)
        print(success)
        # Exit if there were no good signals
        # If success == 1 it means that at least one channel was not available. But this shouldn't stop the rest of the code
        # from running.
        if not success:
            # success = 11: Validated PPF data is already available for all channels
            # success = 8: No good JPF data was found
            # success = 9: JPF data was bad
            logging.error(
                'no KG1V data for pulse {} with uid {}'.format(self.data.pulse,
                                                               self.read_uid))
            return False
            # -------------------------------
        # -------------------------------
        # 4. Read in KG4 data
        # -------------------------------
        logger.info("             Reading in KG4 data.")
        self.data.KG4_data = Kg4Data(self.data.constants)
        self.data.KG4_data.read_data(self.data.MAG_data, self.data.pulse)

        # -------------------------------
        # 5. Read in pellet signals
        # -------------------------------
        logger.info("             Reading in pellet data.")
        self.data.PELLETS_data = PelletData(self.data.constants)
        self.data.PELLETS_data.read_data(self.data.pulse)

        # -------------------------------
        # 6. Read in NBI self.data.
        # -------------------------------
        logger.info("             Reading in NBI data.")
        self.data.NBI_data = NBIData(self.data.constants)
        self.data.NBI_data.read_data(self.data.pulse)

        # -------------------------------
        # 7. Check for a disruption, and set status flag near the disruption to 4
        #    If there was no disruption then dis_time elements are set to -1.
        #    dis_time is a 2 element list, being the window around the disruption.
        #    Within this time window the code will not make corrections.
        # -------------------------------
        logger.info("             Find disruption.")
        is_dis, dis_time = find_disruption(self.data.pulse, self.data.constants,
                                           self.data.KG1_data)
        self.data.is_dis = is_dis
        self.data.dis_time = dis_time[0]
        logger.info("Time of disruption {}".format(dis_time[0]))



        # -------------------------------
        # 8. Read in Be-II signals, and find ELMs
        # -------------------------------
        logger.info("             Reading in ELMs data.")
        self.data.ELM_data = ElmsData(self.data.constants, self.data.pulse, dis_time=dis_time[0])

        # -------------------------------
        # 9. Read HRTS data
        # # -------------------------------
        logger.info("             Reading in HRTS data.")
        self.data.HRTS_data = HRTSData(self.data.constants)
        self.data.HRTS_data.read_data(self.data.pulse)

        # # # # -------------------------------
        # # # 10. Read LIDAR data
        # # # -------------------------------
        logger.info("             Reading in LIDAR data.")
        self.data.LIDAR_data = LIDARData(self.data.constants)
        self.data.LIDAR_data.read_data(self.data.pulse)


        # read status flag

        self.data.SF_list = check_SF(self.read_uid, self.data.pulse)

        [self.data.SF_ch1,
         self.data.SF_ch2,
         self.data.SF_ch3,
         self.data.SF_ch4,
         self.data.SF_ch5,
         self.data.SF_ch6,
         self.data.SF_ch7,
         self.data.SF_ch8] = self.data.SF_list

        self.data.SF_old1 = self.data.SF_ch1
        self.data.SF_old2 = self.data.SF_ch2
        self.data.SF_old3 = self.data.SF_ch3
        self.data.SF_old4 = self.data.SF_ch4
        self.data.SF_old5 = self.data.SF_ch5
        self.data.SF_old6 = self.data.SF_ch6
        self.data.SF_old7 = self.data.SF_ch7
        self.data.SF_old8 = self.data.SF_ch8


        self.data.unval_seq, self.data.val_seq = get_min_max_seq(self.data.pulse, dda="KG1V",
                                                       read_uid=self.read_uid)
        if self.read_uid.lower() == 'jetppf':
            logger.info(
                '{} last public validated seq is {}'.format(str(self.data.pulse),
                                                            str(self.data.val_seq)))
        else:
            logger.info(
                '{} last private validated seq is {}'.format(str(self.data.pulse),
                                                             str(self.data.val_seq)))
            logger.info('userid is {}'.format(self.read_uid))


        # logger.info('unval_seq {}, val_seq {}'.format(str(self.data.unval_seq),str(self.data.val_seq)))
        # save data to pickle into saved folder
        self.save_to_pickle('saved')
        # save data to pickle into scratch folder
        self.save_to_pickle('scratch')
        # save KG1 data on different file (needed later when applying corrections)
        self.save_kg1('saved')
        self.save_kg1('scratch')
        self.data.saved = False
        self.data.data_changed = False
        self.data.statusflag_changed = False
        # dump KG1 data on different file (used to autosave later when applying corrections)
        self.dump_kg1


        if self.data.KG1_data.mode != "Automatic Corrections":
            self.data.KG1_data.correctedby = self.data.KG1_data.mode.split(" ")[2]
            logger.info('{} last validated seq is {} by {}'.format(str(self.data.pulse),
                                                                    str(self.data.val_seq),self.data.KG1_data.correctedby))

        for chan in self.data.KG1_data.density.keys():
            logger.log(5,'enabling channel {}'.format(chan))
            self.tabWidget.setTabEnabled(chan-1, True)

        logger.log(5, 'enabling tab {}'.format(9))
        self.tabWidget.setTabEnabled(8, True)
        logger.log(5, 'enabling tab {}'.format(10))
        self.tabWidget.setTabEnabled(9, True)
        logger.log(5, 'enabling tab {}'.format(11))
        self.tabWidget.setTabEnabled(10, True)
        logger.log(5, 'enabling tab {}'.format(12))
        self.tabWidget.setTabEnabled(11, True)


        return True

# -----------------------

# -------------------------------
    def plot_data(self):
        """
        handles widgets
        initialises canvas to blank
        sets grid and axes
        plots KG1 data

        :return:
        """

        # -------------------------------
        # PLOT KG1 self.data.
        # -------------------------------

        self.widget_LID1.figure.clear()
        self.widget_LID1.draw()

        self.widget_LID2.figure.clear()
        self.widget_LID2.draw()

        self.widget_LID3.figure.clear()
        self.widget_LID3.draw()

        self.widget_LID4.figure.clear()
        self.widget_LID4.draw()

        self.widget_LID5.figure.clear()
        self.widget_LID5.draw()

        self.widget_LID6.figure.clear()
        self.widget_LID6.draw()

        self.widget_LID7.figure.clear()
        self.widget_LID7.draw()

        self.widget_LID8.figure.clear()
        self.widget_LID8.draw()

        self.widget_LID_14.figure.clear()
        self.widget_LID_14.draw()

        self.widget_LID_58.figure.clear()
        self.widget_LID_58.draw()

        self.widget_LID_ALL.figure.clear()
        self.widget_LID_ALL.draw()

        self.widget_MIR.figure.clear()
        self.widget_MIR.draw()

        # define now two gridspecs
        # gs is the gridspec per channels 1-4
        # gs1 is the gridspec for channels 5-8
        # when plotting markers they will allocate space to plot markers in a subplot under current plot

        # gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])# working: creates canvas with 2 columns in the ratio 1/3

        heights = [4]
        gs = gridspec.GridSpec(ncols=1, nrows=1, height_ratios=heights)
        heights1 = [3, 3]
        gs1 = gridspec.GridSpec(ncols=1, nrows=2, height_ratios=heights1)

        ax1 = self.widget_LID1.figure.add_subplot(gs[0]); self.ax1=ax1

        ax2 = self.widget_LID2.figure.add_subplot(gs[0]); self.ax2=ax2

        ax3 = self.widget_LID3.figure.add_subplot(gs[0]); self.ax3=ax3

        ax4 = self.widget_LID4.figure.add_subplot(gs[0]); self.ax4=ax4

        ax5 = self.widget_LID5.figure.add_subplot(gs1[0]); self.ax5=ax5
        ax51 = self.widget_LID5.figure.add_subplot(gs1[1], sharex=ax5); self.ax51=ax51

        ax6 = self.widget_LID6.figure.add_subplot(gs1[0]); self.ax6=ax6
        ax61 = self.widget_LID6.figure.add_subplot(gs1[1], sharex=ax6); self.ax61=ax61

        ax7 = self.widget_LID7.figure.add_subplot(gs1[0]); self.ax7=ax7
        ax71 = self.widget_LID7.figure.add_subplot(gs1[1], sharex=ax7); self.ax71=ax71

        ax8 = self.widget_LID8.figure.add_subplot(gs1[0]); self.ax8=ax8
        ax81 = self.widget_LID8.figure.add_subplot(gs1[1], sharex=ax8); self.ax81=ax81

        ax_all = self.widget_LID_ALL.figure.add_subplot(gs[0]); self.ax_all=ax_all
        ax_14 = self.widget_LID_14.figure.add_subplot(gs[0]); self.ax_14=ax_14
        ax_58 = self.widget_LID_58.figure.add_subplot(gs[0]); self.ax_58=ax_58

        ax_mir = self.widget_MIR.figure.add_subplot(gs[0]); self.ax_mir=ax_mir

        for chan in self.data.KG1_data.density.keys():
            ax_name = 'ax' + str(chan)
            name = 'LID' + str(chan)
            widget_name = 'widget_LID' + str(chan)

            self.data.kg1_norm[chan] = SignalBase(self.data.constants)
            self.data.kg1_norm[chan].data = norm(self.data.KG1_data.density[chan].data)

            vars()[ax_name].plot(self.data.KG1_data.density[chan].time,
                                 self.data.KG1_data.density[chan].data, label=name,
                                 marker='x', color='b', linestyle='None')

            vars()[ax_name].legend()

            ax_all.plot(self.data.KG1_data.density[chan].time,
                        self.data.KG1_data.density[chan].data, label=name,
                        marker='x', linestyle='None')
            ax_all.legend()
            if chan < 5:
                ax_14.plot(self.data.KG1_data.density[chan].time,
                           self.data.KG1_data.density[chan].data, label=name,
                           marker='x', linestyle='None')
                ax_14.legend()

            if chan > 4:
                ax_58.plot(self.data.KG1_data.density[chan].time,
                           self.data.KG1_data.density[chan].data, label=name,
                           marker='x', linestyle='None')
                ax_58.legend()



            if chan > 4:
                name1 = 'MIR' + str(chan)
                name2 = 'JxB' + str(chan)
                ax_name1 = 'ax' + str(chan) + str(1)
                widget_name1 = 'widget_LID' + str(chan) + str(1)
                axx = vars()[ax_name1]
                vars()[ax_name1].plot(self.data.KG1_data.vibration[chan].time,
                                      self.data.KG1_data.vibration[chan].data * 1e6,
                                      marker='x', label=name1, color='b',
                                      linestyle='None')
                vars()[ax_name1].plot(self.data.KG1_data.jxb[chan].time,
                                      self.data.KG1_data.jxb[chan].data * 1e6,
                                      marker='x', label=name2, color='c',
                                      linestyle='None')
                vars()[ax_name1].legend()

                ax_mir.plot(self.data.KG1_data.vibration[chan].time,
                            self.data.KG1_data.vibration[chan].data * 1e6,
                            marker='x', label=name1, linestyle='None')
                ax_mir.legend()
                # draw_widget(chan)

        for chan in self.data.KG1_data.fj_dcn.keys():
            if chan < 9:
                ax_name = 'ax' + str(chan)
                name = 'LID' + str(chan)
                widget_name = 'widget_LID' + str(chan)
                xposition = self.data.KG1_data.fj_dcn[chan].time
                for xc in xposition:
                    vars()[ax_name].axvline(x=xc, color='y', linestyle='--')
            else:
                ax_name = 'ax' + str(chan - 4) + str(1)
                name = 'LID' + str(chan-4)
                widget_name = 'widget_LID' + str(chan)
                xposition = self.data.KG1_data.fj_dcn[chan].time
                for xc in xposition:
                    vars()[ax_name].axvline(x=xc, color='y', linestyle='--')
        for chan in self.data.KG1_data.fj_met.keys():
                ax_name = 'ax' + str(chan)
                name = 'LID' + str(chan)
                widget_name = 'widget_LID' + str(chan)
                xposition = self.data.KG1_data.fj_met[chan].time
                for xc in xposition:
                    vars()[ax_name].axvline(x=xc, color='y', linestyle='--')


        # update canvas
        self.widget_LID1.draw()
        self.widget_LID2.draw()
        self.widget_LID3.draw()
        self.widget_LID4.draw()
        self.widget_LID5.draw()
        self.widget_LID6.draw()
        self.widget_LID7.draw()
        self.widget_LID8.draw()
        self.widget_LID_14.draw()
        self.widget_LID_ALL.draw()
        self.widget_LID_58.draw()
        self.widget_MIR.draw()



    # -----------------------
    def GUI_refresh(self):
        """
        updates GUI after reading data
        enables/disables buttons

        connects tab to tabselected signal

        finally run a check on status flag applied to selected channel
        :return:
        """
        # now status flag group can be enabled
        self.groupBox_statusflag.setEnabled(True)

        # self.button_plot.setEnabled(True)
        # self.button_check_pulse.setEnabled(True)
        self.button_saveppf.setEnabled(True)
        self.button_save.setEnabled(True)
        # self.pushButton_apply.setEnabled(False)
        self.pushButton_makeperm.setEnabled(True)
        self.pushButton_undo.setEnabled(True)
        self.checkSFbutton.setEnabled(True)
        self.comboBox_markers.setEnabled(True)
        self.comboBox_2ndtrace.setEnabled(True)

        self.tabWidget.setCurrentIndex(0)
        self.canvasselected(arg=0)
        self.tabWidget.connect(self.tabWidget,
                               QtCore.SIGNAL("currentChanged(int)"),
                               self.canvasselected)


        # set combobox index to 1 so that the default write_uid is owner
        self.comboBox_writeuid.setCurrentIndex(1)

        self.radioButton_statusflag_0.toggled.connect(
            lambda: self.checkstate(self.radioButton_statusflag_0))

        self.radioButton_statusflag_1.toggled.connect(
            lambda: self.checkstate(self.radioButton_statusflag_1))

        self.radioButton_statusflag_2.toggled.connect(
            lambda: self.checkstate(self.radioButton_statusflag_2))

        self.radioButton_statusflag_3.toggled.connect(
            lambda: self.checkstate(self.radioButton_statusflag_3))

        self.radioButton_statusflag_4.toggled.connect(
            lambda: self.checkstate(self.radioButton_statusflag_4))

        # self.tabWidget.removeTab(3)



#----------------------
    def update_channel(self, chan):
        """
        after a correction is applied this module updates kg1 data to new values
        and replots data on all tabs
        :param chan:
        :return:
        """
        #ax,widget = self.which_tab()
        if chan ==1:
            ax = self.ax1
            widget = self.widget_LID1

            ax.lines[0].set_ydata(self.data.KG1_data.density[chan].data)
            ax.lines[0].set_color('blue')
            # ax.autoscale(enable=True, axis="y", tight=False)
            data = self.data.KG1_data.density[chan].data
            autoscale_data(ax,data)
            self.ax_14.lines[chan-1].set_ydata(self.data.KG1_data.density[chan].data)
            self.ax_all.lines[chan-1].set_ydata(self.data.KG1_data.density[chan].data)
            self.widget_LID_14.draw()
            self.widget_LID_14.flush_events()
            self.widget_LID_ALL.draw()
            self.widget_LID_ALL.flush_events()
            widget.draw()
            widget.flush_events()
            widget.blockSignals(True)

            # ax.yaxis.set_major_locator(MyLocator())


        elif chan ==2:
            ax = self.ax2
            widget = self.widget_LID2
            ax.lines[0].set_ydata(self.data.KG1_data.density[chan].data)
            ax.lines[0].set_color('blue')
            data = self.data.KG1_data.density[chan].data
            autoscale_data(ax,data)
            self.ax_14.lines[chan - 1].set_ydata(
                self.data.KG1_data.density[chan].data)
            self.ax_all.lines[chan - 1].set_ydata(
                self.data.KG1_data.density[chan].data)
            self.widget_LID_14.draw()
            self.widget_LID_14.flush_events()
            self.widget_LID_ALL.draw()
            self.widget_LID_ALL.flush_events()
            widget.draw()
            widget.flush_events()
            widget.blockSignals(True)


        elif chan ==3:
            ax = self.ax3
            widget = self.widget_LID3
            ax.lines[0].set_ydata(self.data.KG1_data.density[chan].data)
            ax.lines[0].set_color('blue')
            data = self.data.KG1_data.density[chan].data
            autoscale_data(ax,data)
            self.ax_14.lines[chan - 1].set_ydata(
                self.data.KG1_data.density[chan].data)
            self.ax_all.lines[chan - 1].set_ydata(
                self.data.KG1_data.density[chan].data)
            self.widget_LID_14.draw()
            self.widget_LID_14.flush_events()
            self.widget_LID_ALL.draw()
            self.widget_LID_ALL.flush_events()
            widget.draw()
            widget.flush_events()
            widget.blockSignals(True)

        elif chan == 4:
            ax = self.ax4
            widget = self.widget_LID4
            ax.lines[0].set_ydata(self.data.KG1_data.density[chan].data)
            ax.lines[0].set_color('blue')
            data = self.data.KG1_data.density[chan].data
            autoscale_data(ax,data)
            self.ax_14.lines[chan - 1].set_ydata(
                self.data.KG1_data.density[chan].data)
            self.ax_all.lines[chan - 1].set_ydata(
                self.data.KG1_data.density[chan].data)
            self.widget_LID_14.draw()
            self.widget_LID_14.flush_events()
            self.widget_LID_ALL.draw()
            self.widget_LID_ALL.flush_events()
            widget.draw()
            widget.flush_events()
            widget.blockSignals(True)

        elif chan == 5:
            ax = self.ax5
            widget = self.widget_LID5
            ax.lines[0].set_ydata(self.data.KG1_data.density[chan].data)
            ax.lines[0].set_color('blue')
            data = self.data.KG1_data.density[chan].data
            autoscale_data(ax,data)
            self.ax_58.lines[0].set_ydata(
                self.data.KG1_data.density[chan].data)
            self.ax_all.lines[chan - 1].set_ydata(
                self.data.KG1_data.density[chan].data)
            ax1 = self.ax51
            ax1.lines[0].set_ydata(self.data.KG1_data.vibration[chan].data* 1e6)
            autoscale_data(ax1, self.data.KG1_data.vibration[chan].data * 1e6)
            ax1.lines[0].set_color('blue')
            self.ax_mir.lines[0].set_ydata(
                self.data.KG1_data.vibration[chan].data* 1e6)
            self.ax_mir.autoscale(axis='y')
            self.widget_LID_58.draw()
            self.widget_LID_58.flush_events()
            self.widget_MIR.draw()
            self.widget_MIR.flush_events()
            self.widget_LID_ALL.draw()
            self.widget_LID_ALL.flush_events()
            widget.draw()
            widget.flush_events()
            widget.blockSignals(True)

        elif chan == 6:
            ax = self.ax6
            widget = self.widget_LID6
            ax.lines[0].set_ydata(self.data.KG1_data.density[chan].data)
            ax.lines[0].set_color('blue')
            data = self.data.KG1_data.density[chan].data
            autoscale_data(ax,data)
            self.ax_58.lines[1].set_ydata(
                self.data.KG1_data.density[chan].data)
            self.ax_all.lines[chan - 1].set_ydata(
                self.data.KG1_data.density[chan].data)
            ax1 = self.ax61
            ax1.lines[0].set_ydata(self.data.KG1_data.vibration[chan].data* 1e6)
            autoscale_data(ax1, self.data.KG1_data.vibration[chan].data * 1e6)
            ax1.lines[0].set_color('blue')
            self.ax_mir.lines[1].set_ydata(
                self.data.KG1_data.vibration[chan].data* 1e6)
            self.widget_LID_58.draw()
            self.widget_LID_58.flush_events()
            self.widget_MIR.draw()
            self.widget_MIR.flush_events()
            self.widget_LID_ALL.draw()
            self.widget_LID_ALL.flush_events()
            widget.draw()
            widget.flush_events()
            widget.blockSignals(True)

        elif chan == 7:
            ax = self.ax7
            widget = self.widget_LID7
            ax.lines[0].set_ydata(self.data.KG1_data.density[chan].data)
            ax.lines[0].set_color('blue')
            data = self.data.KG1_data.density[chan].data
            autoscale_data(ax,data)
            self.ax_58.lines[2].set_ydata(
                self.data.KG1_data.density[chan].data)
            self.ax_all.lines[chan - 1].set_ydata(
                self.data.KG1_data.density[chan].data)
            ax1 = self.ax71
            ax1.lines[0].set_ydata(self.data.KG1_data.vibration[chan].data* 1e6)
            autoscale_data(ax1, self.data.KG1_data.vibration[chan].data * 1e6)
            ax1.lines[0].set_color('blue')
            self.ax_mir.lines[2].set_ydata(
                self.data.KG1_data.vibration[chan].data* 1e6)
            self.widget_LID_58.draw()
            self.widget_LID_58.flush_events()
            self.widget_MIR.draw()
            self.widget_MIR.flush_events()
            self.widget_LID_ALL.draw()
            self.widget_LID_ALL.flush_events()
            widget.draw()
            widget.flush_events()
            widget.blockSignals(True)

        elif chan == 8:
            ax = self.ax8
            widget = self.widget_LID8
            ax.lines[0].set_ydata(self.data.KG1_data.density[chan].data)
            ax.lines[0].set_color('blue')
            data = self.data.KG1_data.density[chan].data
            autoscale_data(ax,data)
            self.ax_58.lines[3].set_ydata(
                self.data.KG1_data.density[chan].data)
            self.ax_all.lines[chan - 1].set_ydata(
                self.data.KG1_data.density[chan].data)
            ax1 = self.ax81
            ax1.lines[0].set_ydata(self.data.KG1_data.vibration[chan].data* 1e6)
            autoscale_data(ax1, self.data.KG1_data.vibration[chan].data* 1e6)
            ax1.lines[0].set_color('blue')
            self.ax_mir.lines[3].set_ydata(
                self.data.KG1_data.vibration[chan].data* 1e6)
            self.widget_LID_58.draw()
            self.widget_LID_58.flush_events()
            self.widget_MIR.draw()
            self.widget_MIR.flush_events()
            self.widget_LID_ALL.draw()
            self.widget_LID_ALL.flush_events()
            widget.draw()
            widget.flush_events()
            widget.blockSignals(True)

        logger.log(5,' updated channhel {}'.format(chan))




    def set_xlimits(self, lower, upper):
        """
        Convenience method to canvas.axes.set_xlim
        as matplotlib autoupdate is bugged

        :param lower: lower limit of data
        :param upper: upper limit of data
        :return:
        """

        self.canvas.axes.set_xlim(lower, upper)
        self.canvas.draw()



# ------------------------

    def plot_2nd_trace(self):
        """
        function that plots a second trace in the tabs(each canvas)
        at the moment clears the canvas and re-plot everything
        so probably a little slow.

        :return:
        """
        # self.data.s2ndtrace = self.comboBox_2ndtrace.itemText(i)
        self.blockSignals(True)
        self.comboBox_markers.setCurrentIndex(0)





        self.data.secondtrace_original = {}
        self.data.secondtrace_norm = {}

        self.data.s2ndtrace = self.comboBox_2ndtrace.currentText()

        # initialize and clean canvas
        self.widget_LID1.figure.clear()
        self.widget_LID1.draw()

        self.widget_LID2.figure.clear()
        self.widget_LID2.draw()

        self.widget_LID3.figure.clear()
        self.widget_LID3.draw()

        self.widget_LID4.figure.clear()
        self.widget_LID4.draw()

        self.widget_LID5.figure.clear()
        self.widget_LID5.draw()

        self.widget_LID6.figure.clear()
        self.widget_LID6.draw()

        self.widget_LID7.figure.clear()
        self.widget_LID7.draw()

        self.widget_LID8.figure.clear()
        self.widget_LID8.draw()

        # self.widget_LID_14.figure.clear()
        # self.widget_LID_14.draw()
        #
        # self.widget_LID_58.figure.clear()
        # self.widget_LID_58.draw()
        #
        # self.widget_LID_ALL.figure.clear()
        # self.widget_LID_ALL.draw()

        # self.widget_MIR.figure.clear()
        # self.widget_MIR.draw()

        heights = [4]
        gs = gridspec.GridSpec(ncols=1, nrows=1, height_ratios=heights)
        heights1 = [3, 3]
        gs1 = gridspec.GridSpec(ncols=1, nrows=2, height_ratios=heights1)

        ax1 = self.widget_LID1.figure.add_subplot(gs[0]); self.ax1=ax1

        ax2 = self.widget_LID2.figure.add_subplot(gs[0]); self.ax2=ax2

        ax3 = self.widget_LID3.figure.add_subplot(gs[0]); self.ax3=ax3

        ax4 = self.widget_LID4.figure.add_subplot(gs[0]); self.ax4=ax4

        ax5 = self.widget_LID5.figure.add_subplot(gs1[0]); self.ax5=ax5
        ax51 = self.widget_LID5.figure.add_subplot(gs1[1], sharex=ax5); self.ax51=ax51

        ax6 = self.widget_LID6.figure.add_subplot(gs1[0]); self.ax6=ax6
        ax61 = self.widget_LID6.figure.add_subplot(gs1[1], sharex=ax6); self.ax61=ax61

        ax7 = self.widget_LID7.figure.add_subplot(gs1[0]); self.ax7=ax7
        ax71 = self.widget_LID7.figure.add_subplot(gs1[1], sharex=ax7); self.ax71=ax71

        ax8 = self.widget_LID8.figure.add_subplot(gs1[0]); self.ax8=ax8
        ax81 = self.widget_LID8.figure.add_subplot(gs1[1], sharex=ax8); self.ax81=ax81

        # for every channel in KG1 (8 channels)
        for chan in self.data.KG1_data.density.keys():
            ax_name = 'ax' + str(chan)
            name = 'LID' + str(chan)

            vars()[ax_name].plot(self.data.KG1_data.density[chan].time,
                                 self.data.KG1_data.density[chan].data,
                                 label=name, marker='x', color='b',
                                 linestyle='None')
            vars()[ax_name].legend()
            # self.widget_LID1.draw()

            if chan > 4:
                name1 = 'MIR' + str(chan)
                name2 = 'JxB' + str(chan)
                ax_name1 = 'ax' + str(chan) + str(1)
                vars()[ax_name1].plot(self.data.KG1_data.vibration[chan].time,
                                      self.data.KG1_data.vibration[chan].data * 1e6,
                                      marker='x', label=name1, color='b',
                                      linestyle='None')
                vars()[ax_name1].plot(self.data.KG1_data.jxb[chan].time,
                                      self.data.KG1_data.jxb[chan].data * 1e6,
                                      marker='x', label=name2, color='c',
                                      linestyle='None')
                vars()[ax_name1].legend()



        for chan in self.data.KG1_data.fj_dcn.keys():
            if chan >9:
                pass
            else:
                ax_name = 'ax' + str(chan)
                name = 'LID' + str(chan)
                widget_name = 'widget_LID' + str(chan)
                xposition = self.data.KG1_data.fj_dcn[chan].time
                for xc in xposition:
                    vars()[ax_name].axvline(x=xc, color='y', linestyle='--')
        for chan in self.data.KG1_data.fj_met.keys():
            if chan >9:
                pass
            else:
                ax_name = 'ax' + str(chan)
                name = 'LID' + str(chan)
                widget_name = 'widget_LID' + str(chan)
                xposition = self.data.KG1_data.fjmet[chan].time
                for xc in xposition:
                    vars()[ax_name].axvline(x=xc, color='y', linestyle='--')


        logger.info('plotting second trace {}'.format(self.data.s2ndtrace))
        if self.data.s2ndtrace == 'None':
            logger.info('no second trace selected')
        elif self.data.s2ndtrace == 'HRTS':
            # check HRTS data exist
            if self.data.HRTS_data is not None:
                # if len(self.data.HRTS_data.density[chan].time) == 0:
                #     logger.info('NO HRTS data')
                # else:
                for chan in self.data.HRTS_data.density.keys():
                    if chan in self.data.KG1_data.density.keys():
                        ax_name = 'ax' + str(chan)
                        name = 'HRTS ch.' + str(chan)
                        # noinspection PyUnusedLocal
                        widget_name = 'widget_LID' + str(chan)

                        self.data.secondtrace_original[chan] = SignalBase(self.data.constants)
                        self.data.secondtrace_norm[chan] = SignalBase(self.data.constants)

                        self.data.secondtrace_original[chan].time = \
                            self.data.HRTS_data.density[chan].time
                        self.data.secondtrace_original[chan].data = \
                            self.data.HRTS_data.density[chan].data
                        # self.data.secondtrace_norm[chan].data = norm(self.data.HRTS_data.density[chan].data)
                        self.data.secondtrace_norm[chan].data = normalise(
                            self.data.HRTS_data.density[chan],
                            self.data.KG1_data.density[chan], self.data.dis_time)

                        vars()[ax_name].plot(self.data.HRTS_data.density[chan].time,
                                             self.data.HRTS_data.density[chan].data,
                                             label=name, marker='o',
                                             color='orange')
                        vars()[ax_name].legend()

            else:
                logging.warning('no {} data'.format(self.data.s2ndtrace))


        elif self.data.s2ndtrace == 'Lidar':
            #if len(self.data.LIDAR_data.density[chan].time) == 0:
            if self.data.LIDAR_data.density is not None:

                for chan in self.data.LIDAR_data.density.keys():
                    if chan in self.data.KG1_data.density.keys():
                        ax_name = 'ax' + str(chan)
                        name = 'Lidar ch.' + str(chan)

                        self.data.secondtrace_original[chan] = SignalBase(self.data.constants)
                        self.data.secondtrace_norm[chan] = SignalBase(self.data.constants)

                        self.data.secondtrace_original[chan].time = \
                            self.data.LIDAR_data.density[chan].time
                        self.data.secondtrace_original[chan].data = \
                            self.data.LIDAR_data.density[chan].data
                        # self.data.secondtrace_norm[chan].data = norm(self.data.LIDAR_data.density[chan].data)
                        self.data.secondtrace_norm[chan].data = normalise(
                            self.data.LIDAR_data.density[chan],
                            self.data.KG1_data.density[chan], self.data.dis_time)

                        vars()[ax_name].plot(self.data.LIDAR_data.density[chan].time,
                                             self.data.LIDAR_data.density[chan].data,
                                             label=name, marker='o',
                                             color='green')
                        vars()[ax_name].legend()


            else:
                logging.warning('no {} data'.format(self.data.s2ndtrace))

        elif self.data.s2ndtrace == 'Far':
            if self.data.KG4_data.faraday is not None:
                # if len(self.data.KG4_data.faraday[chan].time) == 0:
                #     logger.info('NO Far data')
                # else:

                for chan in self.data.KG4_data.faraday.keys():
                    if chan in self.data.KG1_data.density.keys():
                        ax_name = 'ax' + str(chan)
                        name = 'Far ch.' + str(chan)

                        self.data.secondtrace_original[chan] = SignalBase(self.data.constants)
                        self.data.secondtrace_norm[chan] = SignalBase(self.data.constants)

                        self.data.secondtrace_original[chan].time = \
                            self.data.KG4_data.faraday[
                                chan].time
                        self.data.secondtrace_original[chan].data = \
                            self.data.KG4_data.faraday[
                                chan].data
                        # self.data.secondtrace_norm[chan].data = norm(self.data.KG4_data.faraday[chan].data)
                        self.data.secondtrace_norm[chan].data = normalise(
                            self.data.KG4_data.faraday[chan],
                            self.data.KG1_data.density[chan],
                            self.data.dis_time)

                        vars()[ax_name].plot(self.data.KG4_data.faraday[chan].time,
                                             self.data.KG4_data.faraday[chan].data,
                                             label=name, marker='o', color='red')
                        vars()[ax_name].legend()


            else:
                logging.warning('no {} data'.format(self.data.s2ndtrace))


        elif self.data.s2ndtrace == 'CM':
            if self.data.KG4_data.xg_ell_signal is not None:

                # if len(self.data.KG4_data.xg_ell_signal[chan].time) == 0:
                #     logger.info('NO CM data')
                # else:

                for chan in self.data.KG4_data.xg_ell_signal.keys():
                    if chan in self.data.KG1_data.density.keys():
                        ax_name = 'ax' + str(chan)
                        name = 'CM ch.' + str(chan)

                        self.data.secondtrace_original[chan] = SignalBase(self.data.constants)
                        self.data.secondtrace_norm[chan] = SignalBase(self.data.constants)

                        self.data.secondtrace_original[chan].time = \
                            self.data.KG4_data.xg_ell_signal[
                                chan].time
                        self.data.secondtrace_original[chan].data = \
                            self.data.KG4_data.xg_ell_signal[
                                chan].data
                        # self.data.secondtrace_norm[chan].data = norm(
                        #     self.data.KG4_data.xg_ell_signal[chan].data)
                        self.data.secondtrace_norm[chan].data = normalise(
                            self.data.KG4_data.xg_ell_signal[chan],
                            self.data.KG1_data.density[chan],
                            self.data.dis_time)

                        vars()[ax_name].plot(self.data.KG4_data.xg_ell_signal[chan].time,
                                             self.data.KG4_data.xg_ell_signal[chan].data,
                                             label=name, marker='o', color='purple')
                        vars()[ax_name].legend()


            else:
                logging.warning('no {} data'.format(self.data.s2ndtrace))

        elif self.data.s2ndtrace == 'KG1_RT':
            if self.data.KG4_data.density is not None:
                # if len(self.data.KG4_data.density[chan].time) == 0:
                #     logger.info('NO KG1_RT data')
                # else:

                for chan in self.data.KG4_data.density.keys():
                    if chan in self.data.KG1_data.density.keys():
                        ax_name = 'ax' + str(chan)
                        name = 'KG1 RT ch.' + str(chan)

                        self.data.secondtrace_original[chan] = SignalBase(self.data.constants)
                        self.data.secondtrace_norm[chan] = SignalBase(self.data.constants)

                        self.data.secondtrace_original[chan].time = self.data.KG1_data.kg1rt[
                            chan].time
                        self.data.secondtrace_original[chan].data = self.data.KG1_data.kg1rt[
                            chan].data
                        # self.data.secondtrace_norm[chan].data = norm(
                        #     self.data.KG1_data.kg1rt[chan].data)
                        self.data.secondtrace_norm[chan].data = normalise(
                            self.data.KG1_data.kg1rt[chan], self.data.KG1_data.density[chan],
                            self.data.dis_time)

                        vars()[ax_name].plot(self.data.KG1_data.kg1rt[chan].time,
                                             self.data.KG1_data.kg1rt[chan].data,
                                             label=name, marker='o', color='brown')
                        vars()[ax_name].legend()


        elif self.data.s2ndtrace[0:3] == 'LID':
            chan = int(self.data.s2ndtrace[-1])
            name = 'Lid ch.' + str(chan)
            for channel in self.data.KG1_data.density.keys():

                ax_name = 'ax' + str(channel)


                self.data.secondtrace_original[channel] = SignalBase(
                    self.data.constants)
                self.data.secondtrace_norm[channel] = SignalBase(self.data.constants)

                self.data.secondtrace_original[channel].time = \
                self.data.KG1_data.density[
                    chan].time
                self.data.secondtrace_original[channel].data = \
                self.data.KG1_data.density[
                    chan].data
                # self.data.secondtrace_norm[chan].data = norm(
                #     self.data.KG1_data.kg1rt[chan].data)
                self.data.secondtrace_norm[channel].data = normalise(
                    self.data.KG1_data.density[chan],
                    self.data.KG1_data.density[channel],
                    self.data.dis_time)

                vars()[ax_name].plot(self.data.KG1_data.density[chan].time,
                                     self.data.KG1_data.density[chan].data,
                                     label=name, marker='o', color='cyan')
                vars()[ax_name].legend()

                vars()[ax_name].autoscale(enable=True,axis='y',tight=False)




        elif self.data.s2ndtrace == 'BremS':
            logging.error('not implemented yet')


        for chan in self.data.KG1_data.fj_dcn.keys():
            if chan >9:
                pass
            else:
                ax_name = 'ax' + str(chan)
                name = 'LID' + str(chan)
                widget_name = 'widget_LID' + str(chan)
                xposition = self.data.KG1_data.fj_dcn[chan].time
                for xc in xposition:
                    vars()[ax_name].axvline(x=xc, color='y', linestyle='--')
        for chan in self.data.KG1_data.fj_met.keys():
            if chan >9:
                pass
            else:
                ax_name = 'ax' + str(chan)
                name = 'LID' + str(chan)
                widget_name = 'widget_LID' + str(chan)
                xposition = self.data.KG1_data.fjmet[chan].time
                for xc in xposition:
                    vars()[ax_name].axvline(x=xc, color='y', linestyle='--')



        # update canvas
        self.widget_LID1.draw()
        self.widget_LID2.draw()
        self.widget_LID3.draw()
        self.widget_LID4.draw()
        self.widget_LID5.draw()
        self.widget_LID6.draw()
        self.widget_LID7.draw()
        self.widget_LID8.draw()

        # only now activate button "normalize" and "restore"
        self.button_normalize.setEnabled(True)
        self.button_restore.setEnabled(True)
        self.blockSignals(True)

    # ------------------------
    # noinspection PyUnusedLocal,PyUnusedLocal
    @QtCore.pyqtSlot()
    def plot_markers(self):
        """
        function that plots a marker traces in the tabs(each canvas)
        This version creates sub plot inside the canvas
        :return:
        """
        # self.data.s2ndtrace = self.comboBox_2ndtrace.itemText(i)
        self.comboBox_2ndtrace.setCurrentIndex(0)
        self.data.marker = self.comboBox_markers.currentText()

        # self.widget_LID8.draw()

        self.widget_LID1.figure.clear()
        self.widget_LID1.draw()

        self.widget_LID2.figure.clear()
        self.widget_LID2.draw()

        self.widget_LID3.figure.clear()
        self.widget_LID3.draw()

        self.widget_LID4.figure.clear()
        self.widget_LID4.draw()

        self.widget_LID5.figure.clear()
        self.widget_LID5.draw()

        self.widget_LID6.figure.clear()
        self.widget_LID6.draw()

        self.widget_LID7.figure.clear()
        self.widget_LID7.draw()

        self.widget_LID8.figure.clear()
        self.widget_LID8.draw()

        # self.widget_LID_14.figure.clear()
        # self.widget_LID_14.draw()
        #
        # self.widget_LID_58.figure.clear()
        # self.widget_LID_58.draw()
        #
        # self.widget_LID_ALL.figure.clear()
        # self.widget_LID_ALL.draw()

        # self.widget_MIR.figure.clear()
        # self.widget_MIR.draw()

        # ax_all = self.widget_LID_ALL.figure.add_subplot(111)

        # ax_mir = self.widget_MIR.figure.add_subplot(111)

        # define now two gridspecs
        # gs is the gridspec per channels 1-4
        # gs1 is the gridspec for channels 5-8
        # when plotting markers they will allocate space to plot markers in a subplot under current plot

        # gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])# working: creates canvas with 2 columns in the ratio 1/3
        heights = [3, 1]
        gs = gridspec.GridSpec(ncols=1, nrows=2, height_ratios=heights)
        #
        heights1 = [3, 3, 1]
        gs1 = gridspec.GridSpec(ncols=1, nrows=3, height_ratios=heights1)

        ax1 = self.widget_LID1.figure.add_subplot(gs[0]); self.ax1=ax1
        ax1_marker = self.widget_LID1.figure.add_subplot(gs[1], sharex=ax1)
        self.ax1_marker=ax1_marker

        ax2 = self.widget_LID2.figure.add_subplot(gs[0]); self.ax2=ax2
        ax2_marker = self.widget_LID2.figure.add_subplot(gs[1], sharex=ax2)
        self.ax2_marker=ax2_marker

        ax3 = self.widget_LID3.figure.add_subplot(gs[0]); self.ax3=ax3
        ax3_marker = self.widget_LID3.figure.add_subplot(gs[1], sharex=ax3)
        self.ax3_marker=ax3_marker

        ax4 = self.widget_LID4.figure.add_subplot(gs[0]); self.ax4=ax4
        ax4_marker = self.widget_LID4.figure.add_subplot(gs[1], sharex=ax4)
        self.ax4_marker=ax4_marker

        ax5 = self.widget_LID5.figure.add_subplot(gs1[0]); self.ax5=ax5
        ax51 = self.widget_LID5.figure.add_subplot(gs1[1], sharex=ax5); self.ax51=ax51
        ax5_marker = self.widget_LID5.figure.add_subplot(gs1[2], sharex=ax5)
        self.ax5_marker=ax5_marker

        ax6 = self.widget_LID6.figure.add_subplot(gs1[0]); self.ax6=ax6
        ax61 = self.widget_LID6.figure.add_subplot(gs1[1], sharex=ax6); self.ax61=ax61
        ax6_marker = self.widget_LID6.figure.add_subplot(gs1[2], sharex=ax6)
        self.ax6_marker=ax6_marker

        ax7 = self.widget_LID7.figure.add_subplot(gs1[0]); self.ax7=ax7
        ax71 = self.widget_LID7.figure.add_subplot(gs1[1], sharex=ax7); self.ax71=ax71
        ax7_marker = self.widget_LID7.figure.add_subplot(gs1[2], sharex=ax7)
        self.ax7_marker=ax7_marker

        ax8 = self.widget_LID8.figure.add_subplot(gs1[0]); self.ax8=ax8
        ax81 = self.widget_LID8.figure.add_subplot(gs1[1], sharex=ax8); self.ax81=ax81
        ax8_marker = self.widget_LID8.figure.add_subplot(gs1[2], sharex=ax8)
        self.ax8_marker=ax8_marker

        #
        # ax_all = self.widget_LID_ALL.figure.add_subplot(gs[0])
        # ax_14 = self.widget_LID_14.figure.add_subplot(gs[0])
        # ax_58 = self.widget_LID_58.figure.add_subplot(gs[0])

        # ax_mir = self.widget_MIR.figure.add_subplot(gs[0])

        # define now other gridspecs
        # gs2 is the gridspec per channels 1-4
        # gs21 is the gridspec for channels 5-8
        # when plotting NO markers they will reset to standard plots

        heights2 = [4]
        gs2 = gridspec.GridSpec(ncols=1, nrows=1, height_ratios=heights2)
        heights21 = [3, 3]
        gs21 = gridspec.GridSpec(ncols=1, nrows=2, height_ratios=heights21)

        for chan in self.data.KG1_data.density.keys():
            ax_name = 'ax' + str(chan)
            name = 'LID' + str(chan)
            vars()[ax_name].plot(self.data.KG1_data.density[chan].time,
                                 self.data.KG1_data.density[chan].data,
                                 label=name, marker='x', color='b',
                                 linestyle='None')
            vars()[ax_name].legend()
            self.widget_LID1.draw()

            if chan > 4:
                name1 = 'MIR' + str(chan)
                name2 = 'JxB' + str(chan)
                ax_name1 = 'ax' + str(chan) + str(1)
                # noinspection PyUnusedLocal
                widget_name1 = 'widget_LID' + str(chan) + str(1)
                vars()[ax_name1].plot(self.data.KG1_data.vibration[chan].time,
                                      self.data.KG1_data.vibration[chan].data * 1e6,
                                      marker='x', label=name1, color='b',
                                      linestyle='None')
                vars()[ax_name1].plot(self.data.KG1_data.jxb[chan].time,
                                      self.data.KG1_data.jxb[chan].data * 1e6,
                                      marker='x', label=name2, color='c',
                                      linestyle='None')
                vars()[ax_name1].legend()

                # ax_mir.plot(self.data.KG1_data.vibration[chan].time,
                #             self.data.KG1_data.vibration[chan].data * 1e6,
                #             marker='x', label=name1, linestyle='None')
                # ax_mir.legend()
                # draw_widget(chan)

        for chan in self.data.KG1_data.fj_dcn.keys():
            ax_name = 'ax' + str(chan)
            name = 'LID' + str(chan)
            widget_name = 'widget_LID' + str(chan)
            xposition = self.data.KG1_data.fj_dcn[chan].time
            for xc in xposition:
                vars()[ax_name].axvline(x=xc, color='y', linestyle='--')
        for chan in self.data.KG1_data.fj_met.keys():
            ax_name = 'ax' + str(chan)
            name = 'LID' + str(chan)
            widget_name = 'widget_LID' + str(chan)
            xposition = self.data.KG1_data.fjmet[chan].time
            for xc in xposition:
                vars()[ax_name].axvline(x=xc, color='y', linestyle='--')

        # if self.data.marker is not None:
        #     logger.info('plotting marker {}'.format(self.data.marker))
        if self.data.marker == 'None':
            logger.info('no marker selected')

            # if no marker hide axis showing markers
            ax1_marker.set_visible(False)
            ax2_marker.set_visible(False)
            ax3_marker.set_visible(False)
            ax4_marker.set_visible(False)
            ax5_marker.set_visible(False)
            ax6_marker.set_visible(False)
            ax7_marker.set_visible(False)
            ax8_marker.set_visible(False)
            # use the second group of Gridspec and rearrange plots
            ax1.set_position(gs2[0].get_position(self.widget_LID1.figure))
            ax2.set_position(gs2[0].get_position(self.widget_LID2.figure))
            ax3.set_position(gs2[0].get_position(self.widget_LID3.figure))
            ax4.set_position(gs2[0].get_position(self.widget_LID4.figure))

            ax5.set_position(gs21[0].get_position(self.widget_LID5.figure))
            ax51.set_position(gs21[1].get_position(self.widget_LID5.figure))
            ax6.set_position(gs21[0].get_position(self.widget_LID5.figure))
            ax61.set_position(gs21[1].get_position(self.widget_LID5.figure))
            ax7.set_position(gs21[0].get_position(self.widget_LID5.figure))
            ax71.set_position(gs21[1].get_position(self.widget_LID5.figure))
            ax8.set_position(gs21[0].get_position(self.widget_LID5.figure))
            ax81.set_position(gs21[1].get_position(self.widget_LID5.figure))

        elif self.data.marker == 'ELMs':
            logger.info('plotting marker {}'.format(self.data.marker))
            if self.data.ELM_data.elm_times is not None:
                for chan in self.data.KG1_data.density.keys():
                    ax_name = 'ax' + str(chan) + '_marker'
                    # name = 'HRTS ch.' + str(chan)

                    vars()[ax_name].plot(self.data.ELM_data.elms_signal.time,
                                         self.data.ELM_data.elms_signal.data,
                                         color='black')

                    for vert in self.data.ELM_data.elm_times:
                        vars()[ax_name].axvline(x=vert, ymin=0, ymax=1,
                                                linewidth=2, color="red")
                    # if len(self.data.ELM_data.elm_times) > 0:
                    for horz in [self.data.ELM_data.UP_THRESH,
                                 self.data.ELM_data.DOWN_THRESH]:
                        vars()[ax_name].axhline(y=horz, xmin=0, xmax=1,
                                                linewidth=2, color="cyan")
            else:
                logger.info('No ELMs marker')

                # if chan > 4:
                #     ax_name1 = 'ax' + str(chan) + str(1)
                #     widget_name1 = 'widget_LID' + str(chan) + str(1)
                #     vars()[ax_name].plot(
                #         self.data.HRTS_data.density[chan].time,
                #         self.data.HRTS_data.density[chan].data, label=name,
                #         marker='o', color='orange')

        elif self.data.marker == 'MAGNETICs':
            logger.info('plotting marker {}'.format(self.data.marker))
            if (self.data.MAG_data.start_ip) > 0:
                for chan in self.data.KG1_data.density.keys():
                    ax_name = 'ax' + str(chan) + '_marker'
                    # name = 'HRTS ch.' + str(chan)

                    for vert in [self.data.MAG_data.start_ip, self.data.MAG_data.end_ip]:
                        vars()[ax_name].axvline(x=vert, ymin=0, ymax=1,
                                                linewidth=2, color="red",label='Ip')
                    for vert in [self.data.MAG_data.start_flattop,
                                 self.data.MAG_data.end_flattop]:
                        vars()[ax_name].axvline(x=vert, ymin=0, ymax=1,
                                                linewidth=2, color="green",label='flat-top')

                    vars()[ax_name].axvline(x= self.data.dis_time, ymin=0, ymax=1,
                                                linewidth=2, color="brown",label='disruption time')
            else:
                logger.info('No MAGNETICs marker')

        elif self.data.marker == 'NBI':
            logger.info('plotting marker {}'.format(self.data.marker))
            if (self.data.NBI_data.start_nbi) > 0.0:
                for chan in self.data.KG1_data.density.keys():
                    ax_name = 'ax' + str(chan) + '_marker'
                    # name = 'HRTS ch.' + str(chan)

                    for vert in [self.data.NBI_data.start_nbi,
                                 self.data.NBI_data.end_nbi]:
                        vars()[ax_name].axvline(x=vert, ymin=0, ymax=1,
                                                linewidth=2, color="red")
            else:
                logger.info('No NBI marker')

        elif self.data.marker == 'PELLETs':
            logger.info('plotting marker {}'.format(self.data.marker))
            if self.data.PELLETS_data.time_pellets is not None:
                for chan in self.data.KG1_data.density.keys():
                    ax_name = 'ax' + str(chan) + '_marker'
                    # name = 'HRTS ch.' + str(chan)

                    for vert in [self.data.PELLETS_data.time_pellets]:
                        vars()[ax_name].axvline(x=vert, ymin=0, ymax=1,
                                                linewidth=2, color="red")
            else:
                logger.info('No PELLET marker')

        for chan in self.data.KG1_data.fj_dcn.keys():
            ax_name = 'ax' + str(chan)
            name = 'LID' + str(chan)
            widget_name = 'widget_LID' + str(chan)
            xposition = self.data.KG1_data.fj_dcn[chan].time
            for xc in xposition:
                vars()[ax_name].axvline(x=xc, color='y', linestyle='--')
        for chan in self.data.KG1_data.fj_met.keys():
            ax_name = 'ax' + str(chan)
            name = 'LID' + str(chan)
            widget_name = 'widget_LID' + str(chan)
            xposition = self.data.KG1_data.fjmet[chan].time
            for xc in xposition:
                vars()[ax_name].axvline(x=xc, color='y', linestyle='--')

            # pass
        # self.widget_LID1.figure.clear()
        self.widget_LID1.draw()
        #
        # self.widget_LID2.figure.clear()
        self.widget_LID2.draw()
        #
        # self.widget_LID3.figure.clear()
        self.widget_LID3.draw()
        #
        # self.widget_LID4.figure.clear()
        self.widget_LID4.draw()
        #
        # self.widget_LID5.figure.clear()
        self.widget_LID5.draw()
        #
        # self.widget_LID6.figure.clear()
        self.widget_LID6.draw()
        #
        # self.widget_LID7.figure.clear()
        self.widget_LID7.draw()
        #
        # self.widget_LID8.figure.clear()
        self.widget_LID8.draw()


    # -------------------------
    def handle_check_status(self, button_newpulse):
        """
        function used for debugging and control purposes -
        -
        checks if button "newpulse" is clicked
        :param button_newpulse:
        :return: disable/enable combobox
        """

        if button_newpulse.isChecked():
            logger.log(5, '{} is checked'.format(button_newpulse.objectName()))
            self.comboBox_readuid.setEnabled(True)
        else:
                logger.log(5,'{} is NOT checked'.format(button_newpulse.objectName()))
                self.comboBox_readuid.setEnabled(False)

                # ------------------------

    @QtCore.pyqtSlot()
    # ------------------------
    def handle_saveppfbutton(self):

        """
        save data


        user will save either Status Flags or ppf (and SF)

        if user selects in GUI to save ppf a new PPF sequence will be written for dda='KG1V'
        if user selects in GUI to save SF only the SF will be written in the last sequence (no new sequence)
        
        
        is data is has not been modified it automatically switches to save status flags only
        
        as from May 2019 there is a bug in ppfssr so a new ppf will written in either cases.
        


        """

        self.write_uid = self.comboBox_writeuid.currentText()

        # -------------------------------
        # 13. Write data to PPF
        # -------------------------------
        if self.radioButton_storeData.isChecked():
            logger.info(
                ' Requesting to change ppf data\n')
            self.areyousure_window = QtGui.QMainWindow()
            self.ui_areyousure = Ui_areyousure_window()
            self.ui_areyousure.setupUi(self.areyousure_window)
            self.areyousure_window.show()

            ###temporary solution
            logger.warning(
                'writing a new ppf until ppf library is fixed - 20 may 2019\n')
            self.ui_areyousure.pushButton_YES.clicked.connect(
                self.handle_save_data_statusflag)
            self.ui_areyousure.pushButton_NO.clicked.connect(self.handle_no)
            ###end of temporary solution


            # if self.data.data_changed is False:
            #     self.ui_areyousure.pushButton_YES.clicked.connect(
            #         self.handle_save_statusflag)
            #     self.ui_areyousure.pushButton_NO.clicked.connect(self.handle_no)
            # else:



        if self.radioButton_storeSF.isChecked():
            logger.info(
                ' Requesting to change ppf data\n')
            self.areyousure_window = QtGui.QMainWindow()
            self.ui_areyousure = Ui_areyousure_window()
            self.ui_areyousure.setupUi(self.areyousure_window)
            self.areyousure_window.show()

            ###temporary solution
            logger.warning(
                'writing a new ppf until ppf library is fixed - 20 may 2019\n')
            self.ui_areyousure.pushButton_YES.clicked.connect(
                self.handle_save_data_statusflag)
            self.ui_areyousure.pushButton_NO.clicked.connect(self.handle_no)
            ###end of temporary solution
            # if self.read_uid != self.write_uid:
            #     logger.info('read_uid different from write_uid')
            #     logger.info('retrieving sequence numbers for {}'.format{self.write_uid})
            #
            #     self.data.unval_seq, self.data.val_seq = get_min_max_seq(self.data.pulse, dda="KG1V",
            #                                            read_uid=self.write_uid)
            #     if self.data.val_seq <0:
            #         logger.warning('no validated data for user {}\n'.format{self.write_uid})
            #         logger.info('writing new PPF')
            #
            #         self.ui_areyousure.pushButton_YES.clicked.connect(
            #             self.handle_save_data_statusflag)
            #         self.ui_areyousure.pushButton_NO.clicked.connect(
            #             self.handle_no)
            #     else:
            #         self.ui_areyousure.pushButton_YES.clicked.connect(self.handle_save_data_statusflag)
            #         self.ui_areyousure.pushButton_NO.clicked.connect(self.handle_no)
            #
            # else:
            #     self.ui_areyousure.pushButton_YES.clicked.connect(self.handle_save_statusflag)
            #     self.ui_areyousure.pushButton_NO.clicked.connect(self.handle_no)
        elif (self.radioButton_storeSF.isChecked() & self.radioButton_storeData.isChecked()):
            logging.error(' please select action! \n')


    # ------------------------
    @QtCore.pyqtSlot()
    def handle_save_data_statusflag(self):
        """
        function data handles the writing of a new PPF

        :return: 67 if there has been an error in writing status flag
                0 otherwise (success)
        """



        self.checkStatuFlags()

        err = open_ppf(self.data.pulse, self.write_uid)

        if err != 0:
            logger.error('failed to open ppf')
            return 67

        itref_kg1v = -1
        dda = "KG1V"
        return_code = 0





        for chan in self.data.KG1_data.density.keys():
            # status = np.empty(
            #     len(self.data.KG1_data.density[chan].time))
            # status.fill(self.data.SF_list[
            #                 chan - 1])

            # Write signal type
            dtype_type = "TYP{}".format(chan)
            comment = "SIG TYPE: {} CH.{}".format(self.data.KG1_data.type[chan], chan)
            write_err, itref_written = write_ppf(self.data.pulse, dda, dtype_type, np.array([1]),
                                                 time=np.array([0]), comment=comment, unitd=" ", unitt=" ", itref=-1,
                                                 nt=1, status=None)


            dtype_lid = "LID{}".format(chan)
            comment = "DATA FROM KG1 CHANNEL {}".format(chan)
            write_err, itref_written = write_ppf(self.data.pulse, dda, dtype_lid,
                                                 self.data.KG1_data.density[
                                                     chan].data,
                                                 time=self.data.KG1_data.density[
                                                     chan].time,
                                                 comment=comment,
                                                 unitd='M-2', unitt='SEC',
                                                 itref=itref_kg1v,
                                                 nt=len(self.data.KG1_data.density[
                                                            chan].time),
                                                 status=self.data.KG1_data.status[
                                                     chan],
                                                 global_status=self.data.SF_list[
                                                     chan - 1])

            if write_err != 0:
                logger.error(
                    "Failed to write {}/{}. Errorcode {}".format(dda, dtype_lid,
                                                                 write_err))
                break
            if self.data.KG1_data.fj_dcn is not None:
                if chan in self.data.KG1_data.fj_dcn.keys():
                    if self.data.KG1_data.fj_dcn[chan].data.size == 0:
                        del self.data.KG1_data.fj_dcn[chan]

            # Corrected FJs for vertical channels
            if chan <= 4 and chan in self.data.KG1_data.fj_dcn.keys():



                # DCN fringes
                if self.data.KG1_data.fj_dcn is not None:
                    dtype_fc = "FC{}".format(chan)
                    comment = "DCN FRINGE CORRECTIONS CH.{}".format(chan)
                    write_err, itref_written = write_ppf(self.data.pulse, dda,
                                                         dtype_fc,
                                                         self.data.KG1_data.fj_dcn[
                                                             chan].data,
                                                         time=
                                                         self.data.KG1_data.fj_dcn[
                                                             chan].time,
                                                         comment=comment,
                                                         unitd=" ", unitt="SEC",
                                                         itref=itref_kg1v,
                                                         nt=len(
                                                             self.data.KG1_data.fj_dcn[
                                                                 chan].time),
                                                         status=None)

                    if write_err != 0:
                        logger.error(
                            "Failed to write {}/{}. Errorcode {}".format(dda,
                                                                         dtype_fc,
                                                                         write_err))
                        return write_err
                        # break

            # Vibration data and JXB for lateral channels, and corrected FJ
            elif chan > 4 and chan in self.data.KG1_data.vibration.keys():
                if self.data.KG1_data.vibration is not None:
                    # Vibration
                    dtype_vib = "MIR{}".format(chan)
                    comment = "MOVEMENT OF MIRROR {}".format(chan)
                    write_err, itref_written = write_ppf(self.data.pulse, dda,
                                                         dtype_vib,
                                                         self.data.KG1_data.vibration[
                                                             chan].data,
                                                         time=
                                                         self.data.KG1_data.vibration[
                                                             chan].time,
                                                         comment=comment,
                                                         unitd='M', unitt='SEC',
                                                         itref=itref_kg1v,
                                                         nt=len(
                                                             self.data.KG1_data.vibration[
                                                                 chan].time),
                                                         status=
                                                         self.data.KG1_data.status[
                                                             chan -1])
                    if write_err != 0:
                        logger.error(
                            "Failed to write {}/{}. Errorcode {}".format(dda,
                                                                         dtype_vib,
                                                                         write_err))
                        return write_err

                    # JXB movement
                    dtype_jxb = "JXB{}".format(chan)
                    comment = "JxB CALC. MOVEMENT CH.{}".format(chan)
                    write_err, itref_written = write_ppf(self.data.pulse, dda,
                                                         dtype_jxb,
                                                         self.data.KG1_data.jxb[
                                                             chan].data,
                                                         time=self.data.KG1_data.jxb[
                                                             chan].time,
                                                         comment=comment,
                                                         unitd='M', unitt='SEC',
                                                         itref=itref_kg1v,
                                                         nt=len(
                                                             self.data.KG1_data.jxb[
                                                                 chan].time),
                                                         status=
                                                         self.data.KG1_data.status[
                                                             chan -1])

                    if write_err != 0:
                        logger.error(
                            "Failed to write {}/{}. Errorcode {}".format(dda,
                                                                         dtype_jxb,
                                                                         write_err))
                        return write_err
            if self.data.KG1_data.fj_met is not None:
                if chan in self.data.KG1_data.fj_met.keys():
                    if self.data.KG1_data.fj_met[chan].data.size == 0:
                        del self.data.KG1_data.fj_met[chan]

            elif chan > 4 and chan in self.data.KG1_data.fj_met.keys():


                # MET fringes
                if self.data.KG1_data.fj_met is not None:
                    dtype_fc = "MC{} ".format(chan)
                    comment = "MET FRINGE CORRECTIONS CH.{}".format(chan)
                    write_err, itref_written = write_ppf(self.data.pulse, dda,
                                                         dtype_fc,
                                                         self.data.KG1_data.fj_met[
                                                             chan].data,
                                                         time=self.fj_met[
                                                             chan].time,
                                                         comment=comment,
                                                         unitd=" ", unitt="SEC",
                                                         itref=-1,
                                                         nt=len(
                                                             self.data.KG1_data.fj_met[
                                                                 chan].time),
                                                         status=None)

                    if write_err != 0:
                        logger.error(
                            "Failed to write {}/{}. Errorcode {}".format(
                                dda,
                                dtype_fc,
                                write_err))
                        return write_err

        # if write_err != 0:
        #     logger.error('failed to write KG1 ppf')
        #     return 67
        # Write mode DDA

        mode = "Correct.done by {}".format(self.owner)
        dtype_mode = "MODE"
        comment = mode
        write_err, itref_written = write_ppf(self.data.pulse, dda, dtype_mode,
                                             np.array([1]),
                                             time=np.array([0]),
                                             comment=comment, unitd=" ",
                                             unitt=" ", itref=-1, nt=1,
                                             status=None)
        # Retrieve geometry data & write to PPF
        temp, r_ref, z_ref, a_ref, r_coord, z_coord, a_coord, coord_err = self.data.KG1_data.get_coord(
            self.data.pulse)

        if coord_err != 0:
            logger.error('failed to write coord ppf')
            return coord_err

        dtype_temp = "TEMP"
        comment = "Vessel temperature(degC)"
        write_err, itref_written = write_ppf(self.data.pulse, dda, dtype_temp,
                                             np.array([temp]),
                                             time=np.array([0]),
                                             comment=comment, unitd="deg",
                                             unitt="none",
                                             itref=-1, nt=1, status=None)

        geom_chan = np.arange(len(a_ref)) + 1
        dtype_aref = "AREF"
        comment = "CHORD(20 DEC.C): ANGLE"
        write_err, itref_written = write_ppf(self.data.pulse, dda, dtype_aref, a_ref,
                                             time=geom_chan, comment=comment,
                                             unitd="RADIANS", unitt="CHORD NO",
                                             itref=-1, nt=len(geom_chan),
                                             status=None)

        dtype_rref = "RREF"
        comment = "CHORD(20 DEC.C): RADIUS"
        write_err, itref_written = write_ppf(self.data.pulse, dda, dtype_rref, r_ref,
                                             time=geom_chan, comment=comment,
                                             unitd="M", unitt="CHORD NO",
                                             itref=itref_written,
                                             nt=len(geom_chan), status=None)

        dtype_zref = "ZREF"
        comment = "CHORD(20 DEC.C): HEIGHT"
        write_err, itref_written = write_ppf(self.data.pulse, dda, dtype_zref, z_ref,
                                             time=geom_chan, comment=comment,
                                             unitd="M", unitt="CHORD NO",
                                             itref=itref_written,
                                             nt=len(geom_chan), status=None)

        dtype_a = "A   "
        comment = "CHORD: ANGLE"
        write_err, itref_written = write_ppf(self.data.pulse, dda, dtype_a, a_coord,
                                             time=geom_chan, comment=comment,
                                             unitd="RADIANS", unitt="CHORD NO",
                                             itref=itref_written,
                                             nt=len(geom_chan), status=None)

        dtype_r = "R   "
        comment = "CHORD: RADIUS"
        write_err, itref_written = write_ppf(self.data.pulse, dda, dtype_r, r_coord,
                                             time=geom_chan, comment=comment,
                                             unitd="M", unitt="CHORD NO",
                                             itref=itref_written,
                                             nt=len(geom_chan), status=None)

        dtype_z = "Z   "
        comment = "CHORD: HEIGHT"
        write_err, itref_written = write_ppf(self.data.pulse, dda, dtype_z, z_coord,
                                             time=geom_chan, comment=comment,
                                             unitd="M", unitt="CHORD NO",
                                             itref=itref_written,
                                             nt=len(geom_chan), status=None)

        if write_err != 0:
            logger.error('failed to write ppf')
            return 67
        else:
            logger.info("Close PPF.")
            err = close_ppf(self.data.pulse, self.write_uid, self.data.constants.code_version)

        if err != 0:
            logger.error('failed to close ppf')
            return 67

        self.data.saved = True
        self.data.data_changed = True
        self.data.statusflag_changed = True

        self.save_kg1('saved')
        logger.log(5, ' deleting scratch folder')
        delete_files_in_folder('./scratch')
        delete_files_in_folder('./saved')
        logger.log(5, " {} - saved is {} - data changed is {} - status flags changed is {}".format(myself(),self.data.saved,self.data.data_changed, self.data.statusflag_changed))
        self.ui_areyousure.pushButton_YES.setChecked(False)

        self.areyousure_window.hide()
        #
        return return_code

    # ------------------------
    @QtCore.pyqtSlot()
    def handle_save_statusflag(self):
        """
        function that uses ppfssf inside ppf library (ATTENTION this function is not listed yet in the ppf library python documentation (only C++ version)
        :return: 0 if success
                 68 if fails to write status flags
        """

        return_code = 0

        self.checkStatuFlags()
        logger.log(5,"saving data to PPF using this SF list {}".format(self.data.SF_list))
        # Initialise PPF system
        ier = ppfgo(pulse=self.data.pulse)

        if ier != 0:
            return 68

        # Set UID
        ppfuid(self.write_uid, 'w')

        for chan in self.data.KG1_data.density.keys():
            dtype_lid = "LID{}".format(chan)
            # if self.data.val_seq <0:

            (write_err,) = ppfssf(self.data.pulse, self.data.val_seq, 'KG1V', dtype_lid,
                                  self.data.SF_list[chan - 1])


            if write_err != 0:
                logger.error(
                    "Failed to write {}/{} status flag. Errorcode {}".format(
                        'KG1V', dtype_lid,
                        write_err))
                break
            else:
                logger.info(
                    "Status Flag {} written to {}/{} ".format(self.data.SF_list[chan - 1],
                        'KG1V', dtype_lid,
                        ))
        # logger.info("Close PPF.")
        # err = close_ppf(self.data.pulse, self.write_uid,
        #                 self.data.constants.code_version)
        self.ui_areyousure.pushButton_YES.setChecked(False)

        self.areyousure_window.hide()
        logger.info("     Status flags written to ppf.")
        self.data.saved = True
        data_change = True
        self.data.statusflag_changed = True

        self.save_kg1('saved')
        logger.log(5, ' deleting scratch folder')
        delete_files_in_folder('./scratch')

        logger.log(5,
                   " {} - saved is {} - data changed is {} - status flags changed is {}".format(
                       myself(), self.data.saved,
                       self.data.data_changed,
                       self.data.statusflag_changed))
        delete_files_in_folder('./saved')


        return return_code

# ------------------------
    @QtCore.pyqtSlot()
    def handle_normalizebutton(self):
        """
        function that normalises the second trace to KG1 for comparing purposes during validation and fringe correction
        :return:
        """

        if self.data.s2ndtrace == 'None':
            pass
        else:
            logger.info(' Normalizing')
            snd = self.sender()

            self.widget_LID1.figure.clear()
            self.widget_LID1.draw()

            self.widget_LID2.figure.clear()
            self.widget_LID2.draw()

            self.widget_LID3.figure.clear()
            self.widget_LID3.draw()

            self.widget_LID4.figure.clear()
            self.widget_LID4.draw()

            self.widget_LID5.figure.clear()
            self.widget_LID5.draw()

            self.widget_LID6.figure.clear()
            self.widget_LID6.draw()

            self.widget_LID7.figure.clear()
            self.widget_LID7.draw()

            self.widget_LID8.figure.clear()
            self.widget_LID8.draw()

            heights = [4]
            gs = gridspec.GridSpec(ncols=1, nrows=1, height_ratios=heights)
            heights1 = [3, 3]
            gs1 = gridspec.GridSpec(ncols=1, nrows=2, height_ratios=heights1)

            ax1 = self.widget_LID1.figure.add_subplot(gs[0])

            ax2 = self.widget_LID2.figure.add_subplot(gs[0])

            ax3 = self.widget_LID3.figure.add_subplot(gs[0])

            ax4 = self.widget_LID4.figure.add_subplot(gs[0])

            ax5 = self.widget_LID5.figure.add_subplot(gs1[0])
            ax51 = self.widget_LID5.figure.add_subplot(gs1[1], sharex=ax5)

            ax6 = self.widget_LID6.figure.add_subplot(gs1[0])
            ax61 = self.widget_LID6.figure.add_subplot(gs1[1], sharex=ax6)

            ax7 = self.widget_LID7.figure.add_subplot(gs1[0])
            ax71 = self.widget_LID7.figure.add_subplot(gs1[1], sharex=ax7)

            ax8 = self.widget_LID8.figure.add_subplot(gs1[0])
            ax81 = self.widget_LID8.figure.add_subplot(gs1[1], sharex=ax8)

            # ax_all = self.widget_LID_ALL.figure.add_subplot(gs[0])
            # ax_14 = self.widget_LID_14.figure.add_subplot(gs[0])
            # ax_58 = self.widget_LID_58.figure.add_subplot(gs[0])
            #
            # ax_mir = self.widget_MIR.figure.add_subplot(gs[0])
            # ax_mir = self.widget_MIR.figure.add_subplot(gs[0])
            if self.data.s2ndtrace == 'HRTS':
                color = 'orange'
            if self.data.s2ndtrace == 'Lidar':
                color = 'green'
            if self.data.s2ndtrace == 'Far':
                color = 'red'
            if self.data.s2ndtrace == 'CM':
                color = 'purple'
            if self.data.s2ndtrace == 'KG1_RT':
                color = 'brown'
            if self.data.s2ndtrace == 'BremS':
                color = 'grey'
            if self.data.s2ndtrace[0:3] == 'LID':
                color = 'cyan'


            # for every channel in KG1 (8 channels)

            for chan in self.data.KG1_data.density.keys():
                ax_name = 'ax' + str(chan)
                name = 'LID' + str(chan)
                vars()[ax_name].plot(self.data.KG1_data.density[chan].time,
                                     self.data.KG1_data.density[chan].data,
                                     # kg1_norm
                                     label=name, marker='x', color='b',
                                     linestyle='None')
                vars()[ax_name].legend()

                if self.data.s2ndtrace[0:3] == 'LID':
                    name = self.data.s2ndtrace
                else:
                    name = self.data.s2ndtrace + ' ch.' + str(chan)
                vars()[ax_name].plot(self.data.secondtrace_original[chan].time,
                                     self.data.secondtrace_norm[chan].data,
                                     label=name, marker='o',
                                     color=color)
                vars()[ax_name].legend()


                if chan > 4:
                    # channels 5-8 have mirror movement
                    name1 = 'MIR' + str(chan)
                    ax_name1 = 'ax' + str(chan) + str(1)
                    vars()[ax_name1].plot(self.data.KG1_data.vibration[chan].time,
                                          self.data.KG1_data.vibration[
                                              chan].data * 1e6,
                                          marker='x', label=name1, color='b',
                                          linestyle='None')
                    vars()[ax_name1].legend()

            # update canvas
            self.widget_LID1.draw()
            self.widget_LID2.draw()
            self.widget_LID3.draw()
            self.widget_LID4.draw()
            self.widget_LID5.draw()
            self.widget_LID6.draw()
            self.widget_LID7.draw()
            self.widget_LID8.draw()
            # self.widget_LID_14.draw()
            # self.widget_LID_ALL.draw()
            # self.widget_LID_58.draw()
            # self.widget_MIR.draw()
            logger.info(' signals have been normalized')

    # ------------------------
    def handle_button_restore(self):
        """
        function that restores signals to original amplitude
        :return:
        """

        if self.data.s2ndtrace == 'None':
            pass
        else:
            logger.info('restoring signals to original amplitude')
            snd = self.sender()

            self.widget_LID1.figure.clear()
            self.widget_LID1.draw()

            self.widget_LID2.figure.clear()
            self.widget_LID2.draw()

            self.widget_LID3.figure.clear()
            self.widget_LID3.draw()

            self.widget_LID4.figure.clear()
            self.widget_LID4.draw()

            self.widget_LID5.figure.clear()
            self.widget_LID5.draw()

            self.widget_LID6.figure.clear()
            self.widget_LID6.draw()

            self.widget_LID7.figure.clear()
            self.widget_LID7.draw()

            self.widget_LID8.figure.clear()
            self.widget_LID8.draw()

            heights = [4]
            gs = gridspec.GridSpec(ncols=1, nrows=1, height_ratios=heights)
            heights1 = [3, 3]
            gs1 = gridspec.GridSpec(ncols=1, nrows=2, height_ratios=heights1)

            ax1 = self.widget_LID1.figure.add_subplot(gs[0])

            ax2 = self.widget_LID2.figure.add_subplot(gs[0])

            ax3 = self.widget_LID3.figure.add_subplot(gs[0])

            ax4 = self.widget_LID4.figure.add_subplot(gs[0])

            ax5 = self.widget_LID5.figure.add_subplot(gs1[0])
            ax51 = self.widget_LID5.figure.add_subplot(gs1[1], sharex=ax5)

            ax6 = self.widget_LID6.figure.add_subplot(gs1[0])
            ax61 = self.widget_LID6.figure.add_subplot(gs1[1], sharex=ax6)

            ax7 = self.widget_LID7.figure.add_subplot(gs1[0])
            ax71 = self.widget_LID7.figure.add_subplot(gs1[1], sharex=ax7)

            ax8 = self.widget_LID8.figure.add_subplot(gs1[0])
            ax81 = self.widget_LID8.figure.add_subplot(gs1[1], sharex=ax8)

            # ax_all = self.widget_LID_ALL.figure.add_subplot(gs[0])
            # ax_14 = self.widget_LID_14.figure.add_subplot(gs[0])
            # ax_58 = self.widget_LID_58.figure.add_subplot(gs[0])
            #
            # ax_mir = self.widget_MIR.figure.add_subplot(gs[0])
            if self.data.s2ndtrace == 'HRTS':
                color = 'orange'
            if self.data.s2ndtrace == 'Lidar':
                color = 'green'
            if self.data.s2ndtrace == 'Far':
                color = 'red'
            if self.data.s2ndtrace == 'CM':
                color = 'purple'
            if self.data.s2ndtrace == 'KG1_RT':
                color = 'brown'
            if self.data.s2ndtrace == 'BremS':
                color = 'grey'
            # for every channel in KG1 (8 channels)

            for chan in self.data.KG1_data.density.keys():
                ax_name = 'ax' + str(chan)
                name = 'LID' + str(chan)
                vars()[ax_name].plot(self.data.KG1_data.density[chan].time,
                                     self.data.KG1_data.density[chan].data,
                                     label=name, marker='x', color='b',
                                     linestyle='None')
                vars()[ax_name].legend()

                name = self.data.s2ndtrace + ' ch.' + str(chan)
                vars()[ax_name].plot(self.data.secondtrace_original[chan].time,
                                     self.data.secondtrace_original[chan].data,
                                     label=name, marker='o',
                                     color=color)
                vars()[ax_name].legend()
                # self.widget_LID1.draw()

                if chan > 4:
                    # channels 5-8 have mirror movement
                    name1 = 'MIR' + str(chan)
                    ax_name1 = 'ax' + str(chan) + str(1)
                    vars()[ax_name1].plot(self.data.KG1_data.vibration[chan].time,
                                          self.data.KG1_data.vibration[
                                              chan].data * 1e6,
                                          marker='x', label=name1, color='b',
                                          linestyle='None')
                    vars()[ax_name1].legend()

            # update canvas
            self.widget_LID1.draw()
            self.widget_LID2.draw()
            self.widget_LID3.draw()
            self.widget_LID4.draw()
            self.widget_LID5.draw()
            self.widget_LID6.draw()
            self.widget_LID7.draw()
            self.widget_LID8.draw()
            # self.widget_LID_14.draw()
            # self.widget_LID_ALL.draw()
            # self.widget_LID_58.draw()
            # self.widget_MIR.draw()
            logger.info('signals have been restored')





# # ------------------------
    def handle_makepermbutton(self):
        """
        function that makes permanent last correction
        store data into FC dtype only


        :return:

        """
        chan = self.chan
        #if correction is not empty than proceed
        if self.data.KG1_data.density[chan].corrections is not None:
            #check if the corrections applied are already stored, if so overwrite
            for i, value in enumerate(self.data.KG1_data.density[chan].corrections.time):
                found, index = find_in_list_array(
                    self.data.KG1_data.fj_dcn[chan].time, value)
                if found:
                    self.data.KG1_data.fj_dcn[chan].data[index] = self.data.KG1_data.density[chan].corrections.data[i]
                else:
                    self.data.KG1_data.fj_dcn[chan].time = np.append(self.data.KG1_data.fj_dcn[chan].time,self.data.KG1_data.density[chan].corrections.time)
                    self.data.KG1_data.fj_dcn[chan].data = np.append(self.data.KG1_data.fj_dcn[chan].data,self.data.KG1_data.density[chan].corrections.data)
            #emptying corrections
            self.data.KG1_data.density[chan].corrections = SignalBase(self.data.constants)


            index = sorted(range(len(self.data.KG1_data.fj_dcn[chan].time)),key= lambda k: self.data.KG1_data.fj_dcn[chan].time[k])
            self.data.KG1_data.fj_dcn[chan].data = \
            self.data.KG1_data.fj_dcn[chan].data[index]
            self.data.KG1_data.fj_dcn[chan].time = \
            self.data.KG1_data.fj_dcn[chan].time[index]

            self.setcoord(self.chan, reset=True)
        if chan >4:
            if chan + 4 in self.data.KG1_data.fj_dcn.keys():
                for i, value in enumerate(self.data.KG1_data.density[chan].corrections.time):
                    found, index = find_in_list_array(self.data.KG1_data.fj_dcn[chan].time, value)
                    if found:
                        self.data.KG1_data.fj_dcn[chan].data[index] = \
                        self.data.KG1_data.density[chan].corrections.data[i]
                    else:
                        self.data.KG1_data.fj_dcn[chan+4].time = np.append(self.data.KG1_data.fj_dcn[chan+4].time,self.data.KG1_data.density[chan+4].corrections.time)
                        self.data.KG1_data.fj_dcn[chan+4].data = np.append(self.data.KG1_data.fj_dcn[chan+4].data,self.data.KG1_data.density[chan].corrections.data)
                self.data.KG1_data.density[chan+4].corrections = SignalBase(
                    self.data.constants)
                # self.data.KG1_data.density[chan + 4].corrections.time = []
                # self.data.KG1_data.density[chan + 4].corrections.data = []

                index = sorted(range(len(self.data.KG1_data.fj_dcn[chan+4].time)),key=lambda k:self.data.KG1_data.fj_dcn[chan+4].time[k])
                self.data.KG1_data.fj_dcn[chan+4].data = self.data.KG1_data.fj_dcn[chan+4].data[index]

            logger.info('marking correction as permanent')
    # --------------------------
    def check_current_tab(self):
        """
        returns current tab
        :return: current tab
        """
        return self.QTabWidget.currentWidget()


    def keyPressEvent(self, event):
        """
        keyboard events that enable actions are:

        . starts single correction mode
        m stats multiple correction mode
        \ starts zeroing
        n starts neutralisation mode


        :param event: keyboard event
        :return:
        """

        ax, widget = self.which_tab()
        if event.key() == Qt.Key_Period:
            widget.blockSignals(False) # is intended for suppressing QObjects
            # and their subclasses from emitting signals, thus preventing any
            # other objects from receiving them in slots. prevent one object
            # from emitting signals in response to changes that I am making

            #i.e. this is needed to get the event working!

            logger.debug( "{} has been pressed".format(event.text()))
            logger.info('single correction mode')
            self.lineEdit_mancorr.setText("")
            self.getcorrectionpointwidget()
            self.kb.apply_pressed_signal.connect(self.singlecorrection)

        elif event.key() == Qt.Key_M:
            widget.blockSignals(False)
            logger.debug( "{} has been pressed".format(event.text()))
            logger.info('multi correction mode')
            self.lineEdit_mancorr.setText("")
            self.getmultiplecorrectionpointswidget()
            self.kb.apply_pressed_signal.connect(self.multiplecorrections)

        elif event.key() == Qt.Key_N:
            widget.blockSignals(False)
            logger.debug( " {} has been pressed".format(event.text()))
            logger.info('neutralise corrections mode')
            self.lineEdit_mancorr.setText("")
            self.getmultiplecorrectionpointswidget()
            self.kb.apply_pressed_signal.connect(self.neutralisatecorrections)

        elif event.key() == Qt.Key_T:
            widget.blockSignals(False)
            logger.debug( " {} has been pressed".format(event.text()))
            logger.info('zeroing TAIL mode')
            self.getcorrectionpointwidget()
            self.kb.apply_pressed_signal.connect(self.zeroingtail)

        elif event.key() == Qt.Key_Z:
            widget.blockSignals(False)
            logger.debug( " {} has been pressed".format(event.text()))
            logger.info('zeroing INTERVAL mode')
            self.getmultiplecorrectionpointswidget()
            self.kb.apply_pressed_signal.connect(self.zeroinginterval)



        else:
            super(CORMAT_GUI,self).keyPressEvent(event)



    # ----------------------------
    @QtCore.pyqtSlot()
    def handle_help_menu():
        """
        opens Chrome browser to read HTML documentation
        :return:
        """
        import webbrowser
        url = 'file://' + os.path.realpath('../docs/_build/html/index.html')
        webbrowser.get(using='google-chrome').open(url, new=2)

        # ----------------------------

    @QtCore.pyqtSlot()
    def handle_pdf_open():
        """

        :return: opens pdf file of the guide
        """
        file = os.path.realpath('../docs/CORMATpy_GUI_Documentation.pdf')
        import subprocess

        subprocess.Popen(['okular', file])




# -------------------------------
    @pyqtSlot()
    def multiplecorrections(self):
        """
        this module applies multiple corrections (same fringe correction) to selected channel

        :return:
        """

        self.blockSignals(True)
        ax1=self.ax1
        ax2=self.ax2
        ax3=self.ax3
        ax4=self.ax4
        ax5=self.ax5
        ax6=self.ax6
        ax7=self.ax7
        ax8=self.ax8

        self.correction_to_be_applied = self.lineEdit_mancorr.text() # reads correction from gui
        if str(self.chan).isdigit() == True:
            self.chan = int(self.chan)
            time = self.data.KG1_data.density[self.chan].time
            data = self.data.KG1_data.density[self.chan].data
            coord = self.setcoord(self.chan)
        else:
            self.update_channel(self.chan)
            # self.lineEdit_mancorr.setText("")

            self.gettotalcorrections()
            self.pushButton_undo.clicked.connect(self.discard_multiple_points)
            self.kb.apply_pressed_signal.disconnect(self.multiplecorrections)
            self.disconnnet_multiplecorrectionpointswidget()

            self.blockSignals(False)
            return
        if int(self.chan) <5:
            suggested_den = self.suggestcorrection() # computes suggested correction
            try:
                self.corr_den = int(self.lineEdit_mancorr.text()) * self.data.constants.DFR_DCN
            except ValueError:
                logger.error('use numerical values')
                self.lineEdit_mancorr.setText("")
                self.update_channel(self.chan)
                # self.lineEdit_mancorr.setText("")

                self.gettotalcorrections()
                self.pushButton_undo.clicked.connect(
                    self.discard_multiple_points)
                self.kb.apply_pressed_signal.disconnect(
                    self.multiplecorrections)
                self.disconnnet_multiplecorrectionpointswidget()

                self.blockSignals(False)
                return
            if int(suggested_den) != int(self.corr_den):
                logger.warning('suggested correction is different, do you wish to use it?')
                # qm.setDetailedText("suggested correction is "+str(suggested_den))
                ret = qm.question(self, '',
                                  "suggested correction is different: " + str(
                                      suggested_den) + "\n  Do you wish to use it?",
                                  qm.Yes | qm.No)
                # x  = input('y/n?')
                if ret==qm.Yes:

                # x  = input('y/n?')
                # if x.lower() == "y":
                    self.corr_den = suggested_den
                else:
                    pass
        elif  int(self.chan) > 4:
            suggested_den, suggested_vib = self.suggestcorrection()
            try:
                self.corr_den = int(self.lineEdit_mancorr.text().split(",")[0])
                self.corr_vib = int(self.lineEdit_mancorr.text().split(",")[1])

                corrections = self.data.matrix_lat_channels.dot(
                    [self.corr_den, self.corr_vib])
                self.corr_den = corrections[0]
                self.corr_vib = corrections[1]

            except IndexError:
                logger.warning('no vibration correction')
                self.lineEdit_mancorr.setText("")
                self.update_channel(self.chan)
                # self.lineEdit_mancorr.setText("")

                self.gettotalcorrections()
                self.pushButton_undo.clicked.connect(
                    self.discard_multiple_points)
                self.kb.apply_pressed_signal.disconnect(
                    self.multiplecorrections)
                self.disconnnet_multiplecorrectionpointswidget()

                self.blockSignals(False)
                return
            except ValueError:
                logger.error('use numerical values')
                self.lineEdit_mancorr.setText("")
                self.update_channel(self.chan)
                # self.lineEdit_mancorr.setText("")

                self.gettotalcorrections()
                self.pushButton_undo.clicked.connect(
                    self.discard_multiple_points)
                self.kb.apply_pressed_signal.disconnect(
                    self.multiplecorrections)
                self.disconnnet_multiplecorrectionpointswidget()

                self.blockSignals(False)
                return
            if (int(suggested_den) != int(self.corr_den)) & (int(suggested_vib) != int(self.corr_vib)):
                logger.warning('suggested correction is different, do you wish to use it?')
                ret = qm.question(self, '',
                                  "suggested correction is different: " + str(
                                      suggested_den) + ', ' + str(
                                      suggested_vib) + "\n  Do you wish to use it?",
                                  qm.Yes | qm.No)
                # x  = input('y/n?')
                if ret==qm.Yes:
                # x  = input('y/n?')
                # if x.lower() == "y":
                    self.corr_den = suggested_den
                    self.corr_vib = suggested_vib
                else:
                    pass
        ###

        if str(self.chan).isdigit() == True:
            self.chan = int(self.chan)
            time = self.data.KG1_data.density[self.chan].time
            data = self.data.KG1_data.density[self.chan].data
            coord = self.setcoord(self.chan)
        else:
            self.update_channel(self.chan)
            # self.lineEdit_mancorr.setText("")

            self.gettotalcorrections()
            self.pushButton_undo.clicked.connect(self.discard_multiple_points)
            self.kb.apply_pressed_signal.disconnect(self.multiplecorrections)
            self.disconnnet_multiplecorrectionpointswidget()

            self.blockSignals(False)
            return
        # try:
        # pyqt_set_trace()
        for i, value in enumerate(coord):
            logger.log(5, "applying correction @t= {}".format(str(value[0])))
            index, value = find_nearest(time, value[0])
            logger.log(5,
                       " found point where to apply correction at {} with index {}".format(index,
                                                                         value))



            self.data.KG1_data.density[self.chan].correct_fj(
                self.corr_den , index=index
                )
            if self.data.KG1_data.density[self.chan].corrections is not None:
                ax_name = 'ax' + str(self.chan)

                # xposition = self.data.KG1_data.density[self.chan].corrections.time
                # for xc in xposition:
                vars()[ax_name].axvline(x=time[index], color='m', linestyle='--')
                vars()[ax_name].plot(time[index],data[index], 'mo')

            if int(self.chan) > 4:
                try:
                    self.data.KG1_data.vibration[self.chan].correct_fj(
                        self.corr_vib ,
                        time=value)


                except AttributeError:
                    logger.error('insert a correction for the mirror')
                    self.update_channel(self.chan)

                    self.gettotalcorrections()
                    self.pushButton_undo.clicked.connect(
                        self.discard_multiple_points)
                    self.kb.apply_pressed_signal.disconnect(
                        self.multiplecorrections)
                    self.disconnnet_multiplecorrectionpointswidget()

                    self.blockSignals(False)
                    return
        self.update_channel(self.chan)
        self.gettotalcorrections()
        self.pushButton_undo.clicked.connect(self.discard_multiple_points)
        self.kb.apply_pressed_signal.disconnect(self.multiplecorrections)
        self.disconnnet_multiplecorrectionpointswidget()

        self.blockSignals(False)

        logger.warning(
            'remember to mark corrections as permanent before proceeding!')

        ret = qm_permanent.question(self, '',
                          "Mark correction/s as permanent?",
                                    qm_permanent.Yes | qm_permanent.No)

        if ret == qm_permanent.Yes:

            self.handle_makepermbutton()
            self.gettotalcorrections()
        else:
            pass


# # -------------------------------
    @QtCore.pyqtSlot()
    def changezerotail(self, chan,lid, vib, index):
        """
        this function enables the user to change the start time of zeroing of the
        tail of the data

        it just restores previous data using


        :param lid:  density backup
        :param vib: vibration backup
        :param index: index of previous zeroing point
        :return:
        """
        ax1 = self.ax1
        ax2 = self.ax2
        ax3 = self.ax3
        ax4 = self.ax4
        ax5 = self.ax5
        ax6 = self.ax6
        ax7 = self.ax7
        ax8 = self.ax8


        zeroing_time = self.data.KG1_data.density[self.chan].time[int(self.data.zeroing_start[self.chan-1])]
        # logger.log(5, 'old zeroing time t= {}s '.format(zeroing_time))
        tstep = np.mean(
            np.diff(self.data.KG1_data.density[chan].time))
        if int(chan) < 5:  # vertical channels
            self.data.KG1_data.density[chan].data[
            index:] = lid
            self.data.zeroingbackup_den[self.chan-1] = []

            # self.data.xzero_tail = coord[0][0]


            for ch in self.data.KG1_data.density.keys():
                ax_name = 'ax' + str(ch)
                if ch == self.chan:
                    for i, line in enumerate(vars()[ax_name].lines):
                        if abs(line.get_xydata()[0][0]-zeroing_time)<tstep:
                            del vars()[ax_name].lines[i]
                            self.update_channel(int(ch))
                    # vars()[ax_name].axvline(x=xc, color='r', linestyle='--')
                else:
                    for i, line in enumerate(vars()[ax_name].lines):
                        if abs(line.get_xydata()[0][0]-zeroing_time)<tstep:
                            del vars()[ax_name].lines[i]
                    self.update_channel(int(ch))



            self.data.zeroed[chan-1] = False







        elif int(chan) > 4:  # lateral channels
            self.data.KG1_data.density[chan].data[
            index:] = lid
            self.data.KG1_data.vibration[chan].data[
            index:] = vib
            self.data.zeroingbackup_den[self.chan-1] = []
            self.data.zeroingbackup_vib[self.chan-1] = []

            for ch in self.data.KG1_data.density.keys():
                ax_name = 'ax' + str(ch)
                if ch == self.chan:
                    for i, line in enumerate(vars()[ax_name].lines):
                        if abs(line.get_xydata()[0][0]-zeroing_time)<tstep:
                            del vars()[ax_name].lines[i]
                            self.update_channel(int(ch))
                    # vars()[ax_name].axvline(x=xc, color='r', linestyle='--')
                else:
                    for i, line in enumerate(vars()[ax_name].lines):
                        if abs(line.get_xydata()[0][0]-zeroing_time)<tstep:
                            del vars()[ax_name].lines[i]
                    self.update_channel(int(ch))

            self.data.zeroed[chan] = False




    # -------------------------------
    @QtCore.pyqtSlot()
    def zeroingtail(self):
        """
        this module zeroes correction on selected channel

        Permanent corrections will be generated and take effect such that all data points in the interval t>t1 are put as close to zero as possible and the sum of corrections is 0.



        if user is unsatisfied it can be called again to amend previous tail point


        red line will appear on all 8 tabs to show starting point of zeroed data


        ::todo: on other channels must appear smallest t1

        :return:

        """
        # dump KG1 data to pickle file so I can restore data easily
        self.save_kg1('scratch')
        ax1 = self.ax1
        ax2 = self.ax2
        ax3 = self.ax3
        ax4 = self.ax4
        ax5 = self.ax5
        ax6 = self.ax6
        ax7 = self.ax7
        ax8 = self.ax8

        ax_name = 'ax' + str(self.chan)

        # pyqt_set_trace()
        self.blockSignals(True) # signals emitted by this object are blocked

        # self.data.zeroingbackup_den = []
        tstep = np.mean(
            np.diff(self.data.KG1_data.density[self.chan].time))


        if str(self.chan).isdigit() == True:
            self.chan = int(self.chan)
            time = self.data.KG1_data.density[self.chan].time
            data = self.data.KG1_data.density[self.chan].data
            coord = self.setcoord(self.chan) # get point selected from canvas
            M = self.data.matrix_lat_channels
            index, value = find_nearest(time, coord[0][0])  # get nearest point close to selected point in the time array

            zeroing_time = value
            logger.log(5, 'zeroing @t={} s'.format(zeroing_time))
            # zeroing_time = coord[0][0]
            if self.data.zeroed[self.chan-1]:
                #if coord[0][0] != zeroing_time: # check if you point for zeroing if smaller than previous
                    logger.log(5,
                               ' tail zeroing already applied @t={}s changing time'.format(time[int(self.data.zeroing_start[self.chan-1])]))
                    self.changezerotail(self.chan,lid=self.data.zeroingbackup_den[self.chan-1],vib = None,index=int(self.data.zeroing_start[self.chan-1]))





            if  index != self.data.zeroing_start[self.chan-1]:
                self.data.zeroing_start[
                    self.chan-1] = index
                # index of the point where zeroing is applied
                # logger.log(5,'zeroing time is t={}s'.format())

            if int(self.chan) < 5:  # vertical channels
                for idx in range(index,
                                 len(self.data.KG1_data.density[
                                         self.chan].data)):
                    diff = self.data.KG1_data.density[self.chan].data[
                        idx]  # difference between two consecutive points
                    zeroing_correction = int(round((
                                                               diff / self.data.constants.DFR_DCN)))  # check if diff is a fringe jump
                    # logger.log(5,'zeroing correction is {}'.format(zeroing_correction))
                    self.data.zeroingbackup_den[self.chan-1].append(
                        self.data.KG1_data.density[self.chan].data[idx])
                    self.data.KG1_data.density[self.chan].data[idx] = \
                    self.data.KG1_data.density[self.chan].data[
                        idx] - zeroing_correction * self.data.constants.DFR_DCN

                self.remove_corrections_while_zeroing(self.chan,
                                                      index_start=int(self.data.zeroing_start[self.chan-1]),
                                                      index_stop=None)




                xc = zeroing_time
                index_min = int(min(self.data.zeroing_start))
                xc_min = self.data.KG1_data.density[self.chan].time[index_min]
                self.data.zeroed[self.chan-1]=True
                for chan in self.data.KG1_data.density.keys():
                    ax_name = 'ax' + str(chan)
                    if chan == self.chan:
                        if xc!=xc_min:
                            vars()[ax_name].axvline(x=xc, color='r', linestyle='--')
                            vars()[ax_name].axvline(x=xc_min, color='r',
                                                linestyle='--', linewidth=0.25)
                        else:
                            vars()[ax_name].axvline(x=xc, color='r', linestyle='--')
                    else:

                        if self.data.zeroed[chan-1]:#channel already zeroed
                            vars()[ax_name].axvline(x=xc_min, color='r',
                                                    linestyle='--',
                                                    linewidth=0.25)
                        else:#channel not been zeroed

                            for zero_idk,zero_value in enumerate(self.data.zeroing_start):
                                try:
                                    time_zero=time[zero_value]


                                    vars()[ax_name].lines[:] = [x for x in
                                                        vars()[ax_name].lines if
                                                        not abs(
                                                            x.get_xydata()[0][
                                                                0] - time_zero) < tstep]

                                    vars()[ax_name].axvline(x=xc_min, color='r',
                                                        linestyle='--',
                                                        linewidth=0.25)

                                except IndexError:
                                    pass
                        # self.update_channel(chan)

                self.update_channel(self.chan)

                self.pushButton_undo.clicked.connect(self.unzerotail)
                self.kb.apply_pressed_signal.disconnect(self.zeroingtail)
                # if self.data.KG1_data.fj_dcn[self.chan].data.size == 0:
                #      del self.data.KG1_data.fj_dcn[self.chan]
                self.blockSignals(False)

                return


            elif int(self.chan) > 4:  # lateral channels
                for idx in range(index,
                                 len(self.data.KG1_data.density[
                                         self.chan].data)):
                    diff_den = self.data.KG1_data.density[self.chan].data[idx]
                    diff_vib = self.data.KG1_data.vibration[self.chan].data[idx]

                    zeroing_correction = self.data.Minv.dot(np.array([diff_den,
                                                                      diff_vib]))  # get suggested correction by solving linear problem Ax=b
                    zeroing_correction = np.around(zeroing_correction)
                    zeroing_den = int((zeroing_correction[0]))
                    zeroing_vib = int((zeroing_correction[1]))
                    # logger.log(5, 'zeroing correction is {} ,{}'.format(
                    #     zeroing_den,zeroing_vib))
                    self.data.zeroingbackup_den[self.chan-1].append(
                        self.data.KG1_data.density[self.chan].data[idx])

                    self.data.zeroingbackup_vib.append(
                        self.data.KG1_data.vibration[self.chan].data[idx])

                    self.data.KG1_data.density[self.chan].data[idx] = \
                    self.data.KG1_data.density[self.chan].data[idx] - \
                    M.dot([zeroing_den, zeroing_vib])[0]

                    self.data.KG1_data.vibration[self.chan].data[idx] = \
                    self.data.KG1_data.vibration[self.chan].data[idx] - \
                    M.dot([zeroing_den, zeroing_vib])[1]

                self.remove_corrections_while_zeroing(self.chan,
                                                      index_start=int(self.data.zeroing_start[self.chan-1]),
                                                      index_stop=None)



                # zeroing_time = coord[0][0]

                xc = zeroing_time
                index_min = int(min(self.data.zeroing_start))
                xc_min = self.data.KG1_data.density[self.chan].time[index_min]


                self.data.zeroed[self.chan-1]=True
                for chan in self.data.KG1_data.density.keys():
                    ax_name = 'ax' + str(chan)
                    if chan == self.chan:
                        if xc!=xc_min:
                            vars()[ax_name].axvline(x=xc, color='r', linestyle='--')
                            vars()[ax_name].axvline(x=xc_min, color='r',
                                                linestyle='--', linewidth=0.25)
                        else:
                            vars()[ax_name].axvline(x=xc, color='r', linestyle='--')
                    else:

                        if self.data.zeroed[chan-1]:#channel already zeroed
                            vars()[ax_name].axvline(x=xc_min, color='r',
                                                    linestyle='--',
                                                    linewidth=0.25)
                        else:#channel not been zeroed

                            for zero_idk,zero_value in enumerate(self.data.zeroing_start):
                                try:
                                    time_zero=time[zero_value]


                                    vars()[ax_name].lines[:] = [x for x in
                                                        vars()[ax_name].lines if
                                                        not abs(
                                                            x.get_xydata()[0][
                                                                0] - time_zero) < tstep]

                                    vars()[ax_name].axvline(x=xc_min, color='r',
                                                        linestyle='--',
                                                        linewidth=0.25)

                                except IndexError:
                                    pass


                self.update_channel(self.chan)
                self.pushButton_undo.clicked.connect(self.unzerotail)
                self.kb.apply_pressed_signal.disconnect(self.zeroingtail)
                # if self.data.KG1_data.fj_dcn[self.chan].data.size == 0:
                #      del self.data.KG1_data.fj_dcn[self.chan]
                self.blockSignals(False)

                return

            else:
                # self.pushButton_undo.clicked.connect(self.unzerotail)
                self.kb.apply_pressed_signal.disconnect(self.zeroingtail)
                self.blockSignals(False)
                return


        else:
            self.update_channel(self.chan)
            # self.pushButton_undo.clicked.connect(self.unzerotail)
            self.kb.apply_pressed_signal.disconnect(self.zeroingtail)
            self.blockSignals(False)
            return


# -------------------------------
    @QtCore.pyqtSlot()
    def unzerotail(self):
        """
        once user has set a point to zero tail of data. action can be undo

        This module restores data before zeroing of tail was invoked

        works only after a tail event


        :return:
        """

        ax1 = self.ax1
        ax2 = self.ax2
        ax3 = self.ax3
        ax4 = self.ax4
        ax5 = self.ax5
        ax6 = self.ax6
        ax7 = self.ax7
        ax8 = self.ax8


        if str(self.chan).isdigit() == True:
            chan = int(self.chan)
            time = self.data.KG1_data.density[chan].time
            data = self.data.KG1_data.density[chan].data

            coord = self.setcoord(self.chan)

            if is_empty(coord):
                logger.error(
                    'nothing to undo')
                return
            else:

                self.setcoord(self.chan,reset=True)
            zeroing_time = self.data.KG1_data.density[self.chan].time[
                int(self.data.zeroing_start[self.chan-1])]
            M = self.data.matrix_lat_channels
            index, value = find_nearest(time, coord[0][
                0])  # get nearest point close to selected point in the time array

            if int(self.chan) < 5:  # vertical channels
                self.data.KG1_data.density[self.chan].data[
                int(self.data.zeroing_start[self.chan-1]):] = self.data.zeroingbackup_den[self.chan-1]
                self.data.zeroingbackup_den[self.chan-1] = []







            elif int(self.chan) > 4:  # lateral channels
                self.data.KG1_data.density[self.chan].data[
                int(self.data.zeroing_start[self.chan-1]):] = self.data.zeroingbackup_den[self.chan-1]
                self.data.KG1_data.vibration[self.chan].data[
                int(self.data.zeroing_start[self.chan-1]):] = self.data.zeroingbackup_vib[self.chan-1]
                self.data.zeroingbackup_den[self.chan-1] = []
                self.data.zeroingbackup_vib[self.chan-1] = []

            #removing zeroing red line
            tstep = np.mean(
                np.diff(self.data.KG1_data.density[chan].time))
            for chan in self.data.KG1_data.density.keys():
                ax_name = 'ax' + str(chan)
                # for i, line in enumerate(vars()[ax_name].lines):
                #     if chan ==self.chan:
                #         if line.get_xydata()[0][0] == zeroing_time:
                #             del vars()[ax_name].lines[i]
                #     else:
                #         if abs(line.get_xydata()[0][0] -self.data.KG1_data.density[self.chan].time[int(self.data.zeroing_start[self.chan-1])])<tstep:
                #             del vars()[ax_name].lines[i]
                #         elif abs(line.get_xydata()[0][0] - zeroing_time)<tstep:
                #             del vars()[ax_name].lines[i]
                if chan == self.chan:
                    vars()[ax_name].lines[:] = [x for x in vars()[ax_name].lines if not abs(
                        x.get_xydata()[0][0] - zeroing_time) < tstep]
                else:
                    vars()[ax_name].lines[:] = [x for x in vars()[ax_name].lines if not abs(
                        x.get_xydata()[0][0] - zeroing_time) < tstep]
                    vars()[ax_name].lines[:] = [x for x in vars()[ax_name].lines if not abs(
                        x.get_xydata()[0][0] - zeroing_time) < tstep]

            #restoring intershot correction markers
            self.load_pickle(kg1only=True)
            ax_name = 'ax' + str(self.chan)

            if self.chan in self.data.KG1_data.fj_dcn:
                ax_name = 'ax' + str(self.chan)
                for i, xc in enumerate(self.data.KG1_data.fj_dcn[self.chan].time):
                    if xc >= zeroing_time:
                        vars()[ax_name].axvline(x=xc, color='y', linestyle='--')

            self.data.zeroed[self.chan-1] = False
            self.update_channel(int(self.chan))
            self.gettotalcorrections()
            self.pushButton_undo.clicked.disconnect(self.unzerotail)


        else:
            return


#--------------------------
    @QtCore.pyqtSlot()
    def remove_corrections_while_zeroing(self, chan, index_start, index_stop=None):
        """
        function that deals with removing the corrections (permanent and non) from the interval where zeroing is being applyed

        data is dumped to a pickle file for easy restore in case the zeroing will be undo by user




        :param index_start: starting index of zeroing
        :param index_stop: ending index of zeroing (if None is end of data)
        :return: deletes corrections inside given interval
        """
        ax1 = self.ax1
        ax2 = self.ax2
        ax3 = self.ax3
        ax4 = self.ax4
        ax5 = self.ax5
        ax6 = self.ax6
        ax7 = self.ax7
        ax8 = self.ax8

        ax_name = 'ax' + str(chan)

        tstep = np.mean(
            np.diff(self.data.KG1_data.density[chan].time))


        # now I convert the index in a time value
        start_time = self.data.KG1_data.density[chan].time[index_start]
        if index_stop is None:
            stop_time = self.data.KG1_data.density[chan].time[-1]
        else:
            stop_time = self.data.KG1_data.density[chan].time[index_stop]

        # first looking at user corrections (not saved as permanent)
        if self.data.KG1_data.density[
            chan].corrections.data is None:  # if there are no manual corrections (yet) - skip
            logger.debug('no manual corrections at all!')
        elif self.data.KG1_data.density[
            chan].corrections.data.size==0:
            logger.debug('no manual corrections at all!')

        else:
            linestoberemoved = []
            # now looking for the index of the correction
            ind_corr_start, value_start = find_nearest(
                self.data.KG1_data.density[chan].corrections.time, start_time)
            ind_corr_stop, value_stop = find_nearest(
                self.data.KG1_data.density[chan].corrections.time, stop_time)

            # find time values and indexes of corrections within selected range
            indexes_manual, values_manual = find_within_range(
                self.data.KG1_data.density[chan].corrections.time,
                start_time,
                stop_time)  # get time data and indexes of manual corrections
            if (
                    not indexes_manual):  # if there are no manual correction in the selected interval skip

                logger.debug(
                    'no manual corrections inside selected zeroing interval')

            else:
                logger.debug('found manual corrections inside interval')

                if int(chan) <= 4:
                    self.data.KG1_data.density[
                        chan].corrections.data = np.delete(
                        self.data.KG1_data.density[chan].corrections.data,
                        indexes_manual)
                    self.data.KG1_data.density[
                        chan].corrections.time = np.delete(
                        self.data.KG1_data.density[chan].corrections.time,
                        indexes_manual)
                else:
                    self.data.KG1_data.density[
                        chan].corrections.data = np.delete(
                        self.data.KG1_data.density[chan].corrections.data,
                        indexes_manual)
                    self.data.KG1_data.density[
                        chan].corrections.time = np.delete(
                        self.data.KG1_data.density[chan].corrections.time,
                        indexes_manual)

                    self.data.KG1_data.density[
                        chan].corrections.data = np.delete(
                        self.data.KG1_data.vibration[chan].corrections.data,
                        indexes_manual)
                    self.data.KG1_data.density[
                        chan].corrections.time = np.delete(
                        self.data.KG1_data.vibration[chan].corrections.time,
                        indexes_manual)

                num_of_correction = 1  # removing last line
                for j, value in enumerate(values_manual):
                    for i, line in enumerate(vars()[ax_name].lines):
                            logger.log(5, "evaluating line @ {}s".format(
                            line.get_xydata()[0][0]))


                        # if abs(line.get_xydata()[i][0] > value)<tstep:
                            if ((line.get_xydata()[0][0] > start_time) & (line.get_xydata()[0][0] <= stop_time)):
                                logger.log(5," removing line @ {}s".format(value))
                                # del vars()[ax_name].lines[i]
                                #
                                # if abs(line.get_xydata()[0][0] - value) < tstep:
                                #     logger.log(5,
                                #                " removing line @ {}s".format(value))
                                linestoberemoved.append(i)
                dummy=set(linestoberemoved)
                linestoberemoved = list(dummy)
                for x in reversed(linestoberemoved):
                        del vars()[ax_name].lines[x]
                # for i, line in enumerate(vars()[ax_name].lines):
                #     for j, value in enumerate(values_manual):
                #         if line.get_xydata()[0][0] == value:
                #             del vars()[ax_name].lines[i]


                # for i, line in enumerate(vars()[ax_name].lines):
                #     logger.log(5, "evaluating line @ {}s".format(
                #         line.get_xydata()[0][0]))
                #     for j, value in enumerate(values_manual):
                #
                #         # if abs(line.get_xydata()[i][0] > value)<tstep:
                #         if ((line.get_xydata()[0][0] > start_time) & (line.get_xydata()[0][0] <= stop_time)):
                #             logger.log(5," removing line @ {}s".format(value))
                #             del vars()[ax_name].lines[i]

        # now looking at permanent correction and intershot corrections
        # first looking at user corrections (not saved as permanent)
        # if self.data.KG1_data.fj_dcn[chan].data is None:  # if there are no manual corrections (yet) - skip
        if chan not in self.data.KG1_data.fj_dcn.keys() :
                logger.debug('no intershot corrections at all!')

        elif self.data.KG1_data.fj_dcn[chan].time.size ==0:
            logger.debug('no intershot corrections at all!')

        else:
            linestoberemoved = []
            # now looking for the index of the correction
            ind_corr_start, value_start = find_nearest(
                self.data.KG1_data.fj_dcn[chan].time, start_time)
            ind_corr_stop, value_stop = find_nearest(
                self.data.KG1_data.fj_dcn[chan].time, stop_time)
            # find time values and indexes of corrections within selected range
            indexes_automatic, values_automatic = find_within_range(
                self.data.KG1_data.fj_dcn[chan].time,
                start_time,
                stop_time)  # get time data and indexes of intershot corrections
            if (
                    not indexes_automatic):  # if there are no intershot correction in the selected interval skip

                logger.debug(
                    'no intershot corrections inside selected zeroing interval')

            else:
                logger.debug('found intershot corrections inside interval')
                # for ind_corr in range(ind_corr_start, ind_corr_stop):
                if int(chan) <= 4:
                    self.data.KG1_data.fj_dcn[
                        chan].data = np.delete(
                        self.data.KG1_data.fj_dcn[chan].data,
                        indexes_automatic)
                    self.data.KG1_data.fj_dcn[
                        chan].time = np.delete(
                        self.data.KG1_data.fj_dcn[chan].time,
                        indexes_automatic)
                else:
                    self.data.KG1_data.fj_dcn[
                        chan].data = np.delete(
                        self.data.KG1_data.fj_dcn[chan].data,
                        indexes_automatic)
                    self.data.KG1_data.fj_dcn[
                        chan].time = np.delete(
                        self.data.KG1_data.fj_dcn[chan].time,
                        indexes_automatic)
                    if chan + 4 in self.data.KG1_data.fj_dcn.keys():
                        self.data.KG1_data.fj_dcn[
                            chan + 4].data = np.delete(
                            self.data.KG1_data.fj_dcn[
                                chan + 4].data,
                            indexes_automatic)
                        self.data.KG1_data.fj_dcn[
                            chan + 4].time = np.delete(
                            self.data.KG1_data.fj_dcn[
                                chan + 4].time,
                            indexes_automatic)

                for j, value in enumerate(values_automatic):
                    for i, line in enumerate(vars()[ax_name].lines):
                            logger.log(5, "evaluating line @ {}s".format(
                            line.get_xydata()[0][0]))


                        # if abs(line.get_xydata()[i][0] > value)<tstep:
                            if ((line.get_xydata()[0][0] > start_time) & (line.get_xydata()[0][0] <= stop_time)):
                                logger.log(5," removing line @ {}s".format(value))
                                # del vars()[ax_name].lines[i]
                                #
                                # if abs(line.get_xydata()[0][0] - value) < tstep:
                                #     logger.log(5,
                                #                " removing line @ {}s".format(value))
                                linestoberemoved.append(i)
                dummy=set(linestoberemoved)
                linestoberemoved = list(dummy)
                for x in reversed(linestoberemoved):
                        del vars()[ax_name].lines[x]
    # -------------------------------
    @QtCore.pyqtSlot()
    def zeroinginterval(self):
        # -------------------------------

        """
        this module zeroes data on selected channel inside a chosen interval

        Permanent corrections will be generated and take effect such that all data points in the interval t2<t>t1 are put as close to zero as possible and the sum of corrections is 0.

        it is possible to zero multiple interval

        undo button click will undo just last action (i.e. last zeroed interval)


        ::todo: on other channels must appear smallest t1 and largest t2


        :return:
        """
        ax1 = self.ax1
        ax2 = self.ax2
        ax3 = self.ax3
        ax4 = self.ax4
        ax5 = self.ax5
        ax6 = self.ax6
        ax7 = self.ax7
        ax8 = self.ax8



        self.data.zeroingbackup_den[self.chan-1] = []
        self.data.zeroingbackup_vib[self.chan-1] = []

        # pyqt_set_trace()
        self.blockSignals(True) # signals emitted by this object are blocked
        # self.gettotalcorrections()




        if str(self.chan).isdigit() == True:
            self.chan = int(self.chan)
            time = self.data.KG1_data.density[self.chan].time
            data = self.data.KG1_data.density[self.chan].data
            coord = self.setcoord(self.chan) # get point selected from canvas
            if is_empty(coord):
                logger.error(
                    'no interval selected!')
                return
        else:
            self.update_channel(self.chan)
            self.pushButton_undo.clicked.connect(self.unzeroinginterval)
            self.kb.apply_pressed_signal.disconnect(self.zeroinginterval)
            self.disconnnet_multiplecorrectionpointswidget()
            self.blockSignals(False)
            return

        min_coord = min(coord)
        max_coord = max(coord)


        M = self.data.matrix_lat_channels
        index_start, value_start = find_nearest(time, min_coord[0])  # get nearest point close to selected point in the time array
        index_stop, value_stop = find_nearest(time, max_coord[0]) #get nearest point close to selected point in the time array

        logger.info('zeroing chan. {} between t1= {}s and t2= {}s'.format(self.chan,value_start,value_stop))
        self.data.zeroing_start[self.chan-1] = index_start
        self.data.zeroing_stop[self.chan-1] = index_stop

        xc = min_coord[0]
        xc1 = max_coord[0]

        min_zeroing = time[int(min(self.data.zeroing_start))] #minimum zeroing point across channels
        max_zeroing = time[int(max(self.data.zeroing_start))] #maximum zeroing point across channels






        if int(self.chan) <5: # vertical channels
            for idx in range(index_start,index_stop):

                diff =  self.data.KG1_data.density[self.chan].data[idx] # difference between two consecutive points
                zeroing_correction = int(round((diff /self.data.constants.DFR_DCN))) # check if diff is a fringe jump
                # logger.log(5,'zeroing correction is {}'.format(zeroing_correction))
                self.data.zeroingbackup_den[self.chan-1].append(self.data.KG1_data.density[self.chan].data[idx])
                self.data.KG1_data.density[self.chan].data[idx] = self.data.KG1_data.density[self.chan].data[idx] - zeroing_correction*self.data.constants.DFR_DCN
            self.remove_corrections_while_zeroing(self.chan,
                                                  index_start=int(self.data.zeroing_start[self.chan-1]),
                                                  index_stop=int(self.data.zeroing_stop[self.chan-1]))



                # for xc in xposition:
            for chan in self.data.KG1_data.density.keys():
                ax_name = 'ax' + str(self.chan)
                if chan == self.chan:
                    vars()[ax_name].axvline(x=xc, color='r', linestyle='--')
                    vars()[ax_name].axvline(x=xc1, color='r', linestyle='--')
                    vars()[ax_name].axvline(x=min_zeroing, color='r',
                                            linestyle='--',linewidth=0.25)
                    vars()[ax_name].axvline(x=max_zeroing, color='r',
                                            linestyle='--', linewidth=0.25)

                else:
                    vars()[ax_name].axvline(x=min_zeroing, color='r', linestyle='--',linewidth=0.25)
                    vars()[ax_name].axvline(x=max_zeroing, color='r', linestyle='--',linewidth=0.25)
                    self.update_channel(int(chan))

            # self.gettotalcorrections()

            self.update_channel(self.chan)
            self.pushButton_undo.clicked.connect(self.unzeroinginterval)
            self.kb.apply_pressed_signal.disconnect(self.zeroinginterval)
            self.blockSignals(False)




        elif int(self.chan) > 4: # lateral channels
            for idx in range(index_start,index_stop):
                diff_den =   self.data.KG1_data.density[self.chan].data[idx]
                diff_vib =   self.data.KG1_data.vibration[self.chan].data[idx]





                zeroing_correction = self.data.Minv.dot(np.array([diff_den, diff_vib])) # get suggested correction by solving linear problem Ax=b
                zeroing_correction = np.around(zeroing_correction)
                zeroing_den = int((zeroing_correction[0]))
                zeroing_vib = int((zeroing_correction[1]))


                self.data.zeroingbackup_den[self.chan-1].append(
                    self.data.KG1_data.density[self.chan].data[idx])

                self.data.zeroingbackup_vib.append(
                    self.data.KG1_data.vibration[self.chan].data[idx])

                self.data.KG1_data.density[self.chan].data[idx]= self.data.KG1_data.density[self.chan].data[idx] - M.dot([zeroing_den,zeroing_vib])[0]

                self.data.KG1_data.vibration[self.chan].data[idx] = self.data.KG1_data.vibration[self.chan].data[idx] - M.dot([zeroing_den,zeroing_vib])[1]

            self.remove_corrections_while_zeroing(self.chan,
                                                  index_start=int(self.data.zeroing_start[self.chan-1]),
                                                  index_stop=int(self.data.zeroing_stop[self.chan-1]))

            # for xc in xposition:
            for chan in self.data.KG1_data.density.keys():
                ax_name = 'ax' + str(self.chan)
                if chan == self.chan:
                    vars()[ax_name].axvline(x=xc, color='r', linestyle='--')
                    vars()[ax_name].axvline(x=xc1, color='r', linestyle='--')
                    vars()[ax_name].axvline(x=min_zeroing, color='r',
                                            linestyle='--',linewidth=0.25)
                    vars()[ax_name].axvline(x=max_zeroing, color='r',
                                            linestyle='--', linewidth=0.25)

                else:
                    vars()[ax_name].axvline(x=min_zeroing, color='r',
                                            linestyle='--',linewidth=0.25)
                    vars()[ax_name].axvline(x=max_zeroing, color='r',
                                            linestyle='--', linewidth=0.25)
                    self.update_channel(int(chan))

            # self.gettotalcorrections()
            #     self.update_channel(chan)
            self.update_channel(self.chan)
            self.pushButton_undo.clicked.connect(self.unzeroinginterval)
            self.kb.apply_pressed_signal.disconnect(self.zeroinginterval)
            self.disconnnet_multiplecorrectionpointswidget()
            self.blockSignals(False)
        else:
            self.pushButton_undo.clicked.connect(self.unzeroinginterval)
            self.kb.apply_pressed_signal.disconnect(self.zeroinginterval)
            self.disconnnet_multiplecorrectionpointswidget()
            self.blockSignals(False)



        # return


#------------------------
    # -------------------------------
    @QtCore.pyqtSlot()
    def unzeroinginterval(self):

        """
        once user has zeroed an interval of data. action can be undo

        works only after a zeroing interval event

        :return:
        """

        ax1 = self.ax1
        ax2 = self.ax2
        ax3 = self.ax3
        ax4 = self.ax4
        ax5 = self.ax5
        ax6 = self.ax6
        ax7 = self.ax7
        ax8 = self.ax8




        self.blockSignals(True)
        if str(self.chan).isdigit() == True:
            chan = int(self.chan)
            time = self.data.KG1_data.density[chan].time
            data = self.data.KG1_data.density[chan].data

            coord = self.setcoord(self.chan)

        else:
            self.update_channel(int(self.chan))

            self.pushButton_undo.clicked.disconnect(self.unzeroinginterval)
            self.blockSignals(False)
            return

        min_coord = min(coord)
        max_coord = max(coord)
        tstep = np.mean(
            np.diff(self.data.KG1_data.density[self.chan].time))
        index_start, value_start = find_nearest(time, min_coord[0])  # get nearest point close to selected point in the time array
        index_stop, value_stop = find_nearest(time, max_coord[0]) #get nearest point close to selected point in the time array
        # try:
        if int(self.chan) < 5:  # vertical channels
            self.data.KG1_data.density[self.chan].data[int(self.data.zeroing_start[self.chan-1]):int(self.data.zeroing_stop[self.chan-1])] = self.data.zeroingbackup_den[self.chan-1]
            self.data.zeroingbackup_den[self.chan-1] = []


            # removing zeroing red line
            linestoberemoved = []
            ax_name = 'ax' + str(self.chan)
            for chan in self.data.KG1_data.density.keys():
                logger.log(5,'removing red lines from channel {}'.format(chan))
                ax_name = 'ax' + str(chan)
                for i, line in enumerate(vars()[ax_name].lines):

                    if abs(line.get_xydata()[0][0] - value_start) < tstep:
                        linestoberemoved.append(i)
                    elif abs(line.get_xydata()[0][0] - value_stop) < tstep :
                        linestoberemoved.append(i)
                for x in reversed(linestoberemoved):
                    del vars()[ax_name].lines[x]
                linestoberemoved = []


            self.load_pickle(kg1only=True)

            ax_name = 'ax' + str(self.chan)
            if self.chan in self.data.KG1_data.fj_dcn:
                for i, xc in enumerate(
                        self.data.KG1_data.fj_dcn[self.chan].time):
                    if ((xc >= value_start) &  (xc<=value_stop)):
                        vars()[ax_name].axvline(x=xc, color='y', linestyle='--')



            self.update_channel(int(self.chan))
            self.setcoord(self.chan, reset=True)
            # if self.data.KG1_data.fj_dcn[self.chan].data.size == 0:
            #     del self.data.KG1_data.fj_dcn[self.chan]
            self.pushButton_undo.clicked.disconnect(self.unzeroinginterval)
            self.blockSignals(False)


        elif int(self.chan) > 4:  # lateral channels
            self.data.KG1_data.density[self.chan].data[int(self.data.zeroing_start[self.chan-1]):int(self.data.zeroing_stop[self.chan-1])] = self.data.zeroingbackup_den[self.chan-1]
            self.data.KG1_data.vibration[self.chan].data[int(self.data.zeroing_start[self.chan-1]):int(self.data.zeroing_stop[self.chan-1])] = self.data.zeroingbackup_vib[self.chan-1]

            self.data.zeroingbackup_den[self.chan-1] = []
            self.data.zeroingbackup_vib[self.chan-1] = []


            # removing zeroing red line
            linestoberemoved = []
            ax_name = 'ax' + str(self.chan)
            for chan in self.data.KG1_data.density.keys():
                ax_name = 'ax' + str(chan)
                for i, line in enumerate(vars()[ax_name].lines):

                    if abs(line.get_xydata()[0][0] - value_start) < tstep:
                        linestoberemoved.append(i)
                    elif abs(line.get_xydata()[0][0] - value_stop) < tstep:
                        linestoberemoved.append(i)
                for x in reversed(linestoberemoved):
                    del vars()[ax_name].lines[x]
                linestoberemoved = []

            self.load_pickle(kg1only=True)

            ax_name = 'ax' + str(self.chan)
            if self.chan in self.data.KG1_data.fj_dcn:
                for i, xc in enumerate(
                        self.data.KG1_data.fj_dcn[self.chan].time):
                    if ((xc >= value_start) &  (xc<=value_stop)):
                        vars()[ax_name].axvline(x=xc, color='y', linestyle='--')

            self.update_channel(int(self.chan))
            self.setcoord(self.chan, reset=True)
            self.pushButton_undo.clicked.disconnect(self.unzeroinginterval)
            # if self.data.KG1_data.fj_dcn[self.chan].data.size == 0:
            #     del self.data.KG1_data.fj_dcn[self.chan]
            self.blockSignals(False)
        # except:
        #     # logger.error('error in '.format(inspect.currentframe()))
        #     logger.error('error in '.format(sys._getframe(1)))
        #     self.blockSignals(False)



    @QtCore.pyqtSlot()
    def neutralisatecorrections(self):
        """
        module that neutralises permanent corretions

        first the code will process manual corrections not made permanent yet

        then the code will process automatic corrections produced by hardware and stored inside KG1V/FCx

        :return:
        """

        self.blockSignals(True)
        ax1 = self.ax1
        ax2 = self.ax2
        ax3 = self.ax3
        ax4 = self.ax4
        ax5 = self.ax5
        ax6 = self.ax6
        ax7 = self.ax7
        ax8 = self.ax8
        ax_name = 'ax' + str(self.chan)

        if str(self.chan).isdigit() == True: # if chan is 1-8 then
            self.chan = int(self.chan)
            time = self.data.KG1_data.density[self.chan].time # get time data
            data = self.data.KG1_data.density[self.chan].data # get density data
            coord = self.setcoord(self.chan) # get points selected by user
        else:#the user has run the Neutralise event not on a 1-8 tab
            self.update_channel(self.chan)

            self.gettotalcorrections()
            self.pushButton_undo.clicked.connect(self.discard_neutralise_corrections)
            self.kb.apply_pressed_signal.disconnect(
                self.neutralisatecorrections)
            self.disconnnet_neutralisepointswidget()

            self.blockSignals(False)
            return
        # get coordinates seletecte by user
        min_coord = min(coord)
        max_coord = max(coord)


        if self.data.KG1_data.density[self.chan].corrections.data is None: # if there are no manual corrections (yet) - skip
            self.update_channel(self.chan)
            self.gettotalcorrections()


        else:
            #find time values and indexes of corrections within selected range
            indexes_manual, values_manual = find_within_range(
                self.data.KG1_data.density[self.chan].corrections.time,
                min_coord[0], max_coord[0]) # get time data and indexes of manual corrections
            if (not indexes_manual):# if there are no manual correction in the selected interval skip
                self.update_channel(self.chan)
                self.gettotalcorrections()

            else:

                if self.data.KG1_data.density[
                    self.chan].corrections.time is not None: # if there are corrections in that range

                    corrections_manual = \
                    self.data.KG1_data.density[self.chan].corrections.data[
                        indexes_manual]
                    #change sign
                    corrections_manual_inverted = [x * (-1) for x in
                                                   corrections_manual]

                    logger.info("applying this neutralaisation at {}".format(
                        corrections_manual_inverted))

                    #iterate corrections
                    for i, value in enumerate(values_manual):
                        #find times of correction and index inside time vector
                        index, value = find_nearest(time, value)

                        self.corr_den = int(round(corrections_manual_inverted[i]))

                        time_corr = values_manual[i]



                        logger.log(5,
                                   " found point where to neutralise correction @t= {} with index {}".format(
                                       value,
                                       index))
                        #apply correction
                        self.data.KG1_data.density[self.chan].correct_fj(
                            self.corr_den * self.data.constants.DFR_DCN, index=index
                        )

                        if int(self.chan) > 4: #if is a lateral channel
                            if self.chan+4 in self.data.KG1_data.fj_dcn.keys(): # if there are automatic corrections in the vibration signal
                                self.corr_vib = int(round(self.data.KG1_data.density[self.chan+4].corrections.data[i]))
                            else:
                                self.corr_vib = 0

                            self.data.KG1_data.vibration[
                                    self.chan].correct_fj(
                                    self.corr_vib * self.data.constants.DFR_DCN,
                                    index=index)

                        vars()[ax_name].axvline(x=value, color='g',
                                                linestyle='--')



                    indexes_manual = [x+1 for x in indexes_manual] # first line is kg1 data!
                    for jj, ind in enumerate(reversed(indexes_manual)):
                        # print(jj,ind)
                        if self.chan == 1:
                            # del self.ax1.lines[-(len(self.ax1.lines)):-1]
                            del self.ax1.lines[ind]
                            # del self.ax1.lines[1:]
                        elif self.chan == 2:
                            del self.ax2.lines[ind]
                        elif self.chan == 3:
                            del self.ax3.lines[ind]
                        elif self.chan == 4:
                            del self.ax4.lines[ind]
                        elif self.chan == 5:
                            del self.ax5.lines[ind]
                        elif self.chan == 6:
                            del self.ax6.lines[ind]
                        elif self.chan == 7:
                            del self.ax7.lines[ind]
                        elif self.chan == 8:
                            del self.ax8.lines[ind]




                self.update_channel(self.chan)

                self.gettotalcorrections()






#automatic correction (made by hardware)





        if self.data.KG1_data.fj_dcn[self.chan].data is None:
            # if there are not automatic correction updated channel and close event
            self.update_channel(self.chan)
            self.gettotalcorrections()
            self.pushButton_undo.clicked.connect(self.discard_neutralise_corrections)
            self.kb.apply_pressed_signal.disconnect(
                self.neutralisatecorrections)
            self.disconnnet_multiplecorrectionpointswidget()

            self.blockSignals(False)
            return

        else:
            #find corrections
            indexes_automatic, values_automatic = find_within_range(
                self.data.KG1_data.fj_dcn[self.chan].time, min_coord[0],
                max_coord[0])
            if (not indexes_automatic)  :
                #if no correction in selected range update and close event
                self.update_channel(self.chan)
                self.gettotalcorrections()
            else:
                logger.info("automatic correction times {} \n ".format(self.data.KG1_data.fj_dcn[self.chan].time[indexes_automatic]))
                if self.chan <5:
                    logger.info("automatic correction data {}\n ".format(self.data.KG1_data.fj_dcn[self.chan].data[indexes_automatic]))
                else:
                    #if chan+4 is in fj_dcn means there are automatic corrections for vibration channel
                    if self.chan+4 in self.data.KG1_data.fj_dcn.keys():
                        #find values in range
                        indexes_automatic_vib, values_automatic_vib = find_within_range(
                            self.data.KG1_data.fj_dcn[self.chan+4].time,
                            min_coord[0],
                            max_coord[0])
                        logger.info("automatic correction data {}, {}\n ".format(self.data.KG1_data.fj_dcn[self.chan].data[indexes_automatic],self.data.KG1_data.fj_dcn[self.chan+4].data[indexes_automatic_vib]))
                    else:
                        logger.info("automatic correction data {}\n ".format(
                            self.data.KG1_data.fj_dcn[self.chan].data[
                                indexes_automatic]))

                #create lists of corrections
                corrections = self.data.KG1_data.fj_dcn[self.chan].data[
                    indexes_automatic]
                if (self.chan >4) & (self.chan + 4 in self.data.KG1_data.fj_dcn.keys()):
                    corrections_vib = self.data.KG1_data.fj_dcn[self.chan+4].data[
                        indexes_automatic_vib]

                for i,value in enumerate(corrections):
                    logger.log(5," correction found  @ {}".format(values_automatic[i]))


                corrections_inverted = [x * (-1) for x in corrections]
                logger.info("applying this {} neutralisation/s ".format(
                    corrections_inverted))
                # iterate corrections
                for i, value in enumerate(values_automatic):
                    #look inside time array to find index of the correction
                    index, value_found = find_nearest(time, value)


                    self.corr_den = int(round(corrections_inverted[i]))

                    time_corr =  values_automatic[i]




                    logger.log(5,
                               " found point where to neutralise correction @t= {} with index {}".format(value,index))


                    #for lateral channels
                    if int(self.chan) > 4:
                        #if there is a vibration automatic correction
                        if  (self.chan + 4 in self.data.KG1_data.fj_dcn.keys()):
                            #iterate vibration correction
                            for j,value_vib in enumerate(self.data.KG1_data.fj_dcn[self.chan +4].time[indexes_automatic_vib]):
                                #if time vibration correction is the same
                                if value == value_vib:

                                    self.corr_vib = -int(round(self.data.KG1_data.fj_dcn[self.chan + 4].data[j]))
                                else:
                                    self.corr_vib = 0
                        else:
                                self.corr_vib = 0

                        M = self.data.matrix_lat_channels
                        neutralised_correction = M.dot(np.array([self.corr_den, self.corr_vib]))

                        self.lid = neutralised_correction[0]
                        self.mir = neutralised_correction[1]

                        self.data.KG1_data.density[self.chan].correct_fj(self.lid,index=index,lid=self.corr_den)

                        self.data.KG1_data.vibration[self.chan].correct_fj(self.mir,index=index,lid=self.corr_vib)
                    else:
                        self.data.KG1_data.density[self.chan].correct_fj(self.corr_den * self.data.constants.DFR_DCN,index=index)

                    vars()[ax_name].axvline(x=value, color='g',
                                            linestyle='--')

                indexes_automatic = [x + 1 for x in
                                     indexes_automatic]  # first line is kg1 data!
                for jj, ind in enumerate(reversed(indexes_automatic)):

                    if self.chan == 1:

                        del self.ax1.lines[ind]

                    elif self.chan == 2:
                        del self.ax2.lines[ind]
                    elif self.chan == 3:
                        del self.ax3.lines[ind]
                    elif self.chan == 4:
                        del self.ax4.lines[ind]
                    elif self.chan == 5:
                        del self.ax5.lines[ind]
                    elif self.chan == 6:
                        del self.ax6.lines[ind]
                    elif self.chan == 7:
                        del self.ax7.lines[ind]
                    elif self.chan == 8:
                        del self.ax8.lines[ind]

                self.update_channel(self.chan)

                self.gettotalcorrections()



        self.pushButton_undo.clicked.connect(self.discard_neutralise_corrections)
        self.kb.apply_pressed_signal.disconnect(self.neutralisatecorrections)
        self.disconnnet_multiplecorrectionpointswidget()

        self.blockSignals(False)

        logger.warning('remember to mark corrections as permanent before proceeding!')
        ret = qm_permanent.question(self, '',
                          "Mark correction/s as permanent?",
                                    qm_permanent.Yes | qm_permanent.No)

        if ret == qm_permanent.Yes:

            self.handle_makepermbutton()
            self.gettotalcorrections()
        else:
            pass

    # -------------------------------
    @QtCore.pyqtSlot()
    def suggestcorrection(self):
        """
        module that suggests correction to apply on selected point
        :return:
        """
        if str(self.chan).isdigit() == True:
            # if current channel is a number (1-8 allowed values)
            #then we assign to time and data the values of density for the current channel
                self.chan = int(self.chan)
                time = self.data.KG1_data.density[self.chan].time
                data = self.data.KG1_data.density[self.chan].data
                coord = self.setcoord(self.chan) # get the points selected by the user
                index, value = find_nearest(time, coord[0][0]) #get nearest point close to selected point in the time array

                if int(self.chan) <5: # vertical channels
                    diff =  self.data.KG1_data.density[self.chan].data[index+1] - self.data.KG1_data.density[self.chan].data[index] # difference between two consecutive points
                    suggest_correction = int(round((diff /self.data.constants.DFR_DCN))) # check if diff is a fringe jump
                    logger.info('suggested correction is {}'.format(suggest_correction))
                    return suggest_correction

                elif int(self.chan) > 4: # lateral channels
                    diff_den =  self.data.KG1_data.density[self.chan].data[index+1] - self.data.KG1_data.density[self.chan].data[index]
                    diff_vib =  self.data.KG1_data.vibration[self.chan].data[index+1] - self.data.KG1_data.vibration[self.chan].data[index]





                    suggest_correction = self.data.Minv.dot(np.array([diff_den, diff_vib])) # get suggested correction by solving linear problem Ax=b
                    suggest_correction = np.around(suggest_correction)
                    suggested_den = int((suggest_correction[0]))
                    suggested_vib = int((suggest_correction[1]))

                    logger.info('suggested correction is {} , {}'.format(suggested_den,suggested_vib))
                    return suggested_den,  suggested_vib
    # -------------------------------
    # @QtCore.pyqtSlot()
    # def stopaction(self):
    #     """
    #     manages events after pressing ESC key
    #     STILL NOT WORKING
    #     :return:
    #     """
    #     # print('stop')
    #     logger.log(5, "stopping action")
    #     self.single_correction.disconnect(self.getcorrectionpointwidget)
    #     self.multiple_correction.disconnect(self.getcorrectionpointwidget)
    #     self.zeroing.disconnect(self.zeroingcorrection)
    #     self.unzeroing.disconnect(self.unzeroingcorrection)
    #     # self.stop.disconnect(self.stopactionn)
    #     self.neutralisation_mode.disconnect(self.neutralisatecorrections)
    #     self.suggested_correction.disconnect(self.suggestcorrection)
    #     logger.log(5, "re-establishing connections")
    #     self.create_connections()
    #     QApplication.processEvents()


    # -------------------------------
    @QtCore.pyqtSlot()
    def getcorrectionpointwidget(self):
        """
        action to perform when the single correction signal is emitted:
        each widget (canvas) is connected to the function that gets data point from canvas

        and shows widget to apply correction
        :return:
        """
        self.blockSignals(True)
        if self.current_tab  == 'LID_1':
            self.widget_LID1.signal.connect(self.get_point)
        elif self.current_tab  == 'LID_2':
            self.widget_LID2.signal.connect(self.get_point)
        elif self.current_tab  == 'LID_3':
            self.widget_LID3.signal.connect(self.get_point)
        elif self.current_tab  == 'LID_4':
            self.widget_LID4.signal.connect(self.get_point)
        elif self.current_tab  == 'LID_5':
            self.widget_LID5.signal.connect(self.get_point)
        elif self.current_tab  == 'LID_6':
            self.widget_LID6.signal.connect(self.get_point)
        elif self.current_tab  == 'LID_7':
            self.widget_LID7.signal.connect(self.get_point)
        elif self.current_tab  == 'LID_8':
            self.widget_LID8.signal.connect(self.get_point)
        self.blockSignals(False)
        # #

        self.kb.show()


    # -------------------------------
    @QtCore.pyqtSlot()
    def getmultiplecorrectionpointswidget(self):
        """
        action to perform when the single correction signal is emitted:
        each widget (canvas) is connected to the function that gets data point from canvas

        and shows widget to apply correction
        :return:
        """
        self.blockSignals(True)
        if self.current_tab  == 'LID_1':
            self.setcoord(1, reset=True)
            self.widget_LID1.signal.connect(self.get_multiple_points)

        elif self.current_tab  == 'LID_2':
            self.setcoord(2, reset=True)
            self.widget_LID2.signal.connect(self.get_multiple_points)

        elif self.current_tab  == 'LID_3':
            self.setcoord(3, reset=True)
            self.widget_LID3.signal.connect(self.get_multiple_points)

        elif self.current_tab  == 'LID_4':
            self.setcoord(4, reset=True)
            self.widget_LID4.signal.connect(self.get_multiple_points)

        elif self.current_tab  == 'LID_5':
            self.setcoord(5, reset=True)
            self.widget_LID5.signal.connect(self.get_multiple_points)

        elif self.current_tab  == 'LID_6':
            self.setcoord(6, reset=True)
            self.widget_LID6.signal.connect(self.get_multiple_points)

        elif self.current_tab  == 'LID_7':
            self.setcoord(7, reset=True)
            self.widget_LID7.signal.connect(self.get_multiple_points)

        elif self.current_tab  == 'LID_8':
            self.setcoord(8, reset=True)
            self.widget_LID8.signal.connect(self.get_multiple_points)
        self.blockSignals(False)

        # #

        self.kb.show()


    def disconnnet_multiplecorrectionpointswidget(self):
        """
        action to perform when the single correction signal is emitted:
        each widget (canvas) is connected to the function that gets data point from canvas

        and shows widget to apply correction
        :return:
        """
        if self.current_tab  == 'LID_1':
            self.widget_LID1.signal.disconnect(self.get_multiple_points)
        elif self.current_tab  == 'LID_2':
            self.widget_LID2.signal.disconnect(self.get_multiple_points)
        elif self.current_tab  == 'LID_3':
            self.widget_LID3.signal.disconnect(self.get_multiple_points)
        elif self.current_tab  == 'LID_4':
            self.widget_LID4.signal.disconnect(self.get_multiple_points)
        elif self.current_tab  == 'LID_5':
            self.widget_LID5.signal.disconnect(self.get_multiple_points)
        elif self.current_tab  == 'LID_6':
            self.widget_LID6.signal.disconnect(self.get_multiple_points)
        elif self.current_tab  == 'LID_7':
            self.widget_LID7.signal.disconnect(self.get_multiple_points)
        elif self.current_tab  == 'LID_8':
            self.widget_LID8.signal.disconnect(self.get_multiple_points)

    # def eventFilter(self, obj, event):
    #     logger.log(5, 'EVENT RECEIVED')
    #     logger.log(5, obj, event)
    #     if (obj is self or obj is self.new_action) and event.type() == QtCore.QEvent.Close:
    #         return True
    #     else:
    #         return False
# -------------------------

    @QtCore.pyqtSlot()
    def gettotalcorrections(self):
        if str(self.chan).isdigit() == True:
            self.lineEdit_totcorr.setEnabled(True)
            self.chan = int(self.chan)
            chan = int(self.chan)
            if chan < 5:
                #temporary (not marked as permanent) corrections set by user during validation
                if self.data.KG1_data.density[chan].corrections.data is None:
                    total = 0
                elif self.data.KG1_data.density[chan].corrections.data.size==0:
                    total = 0

                    # self.totalcorrections_den[chan]= total
                else:
                    total = int(round(np.sum(self.data.KG1_data.density[chan].corrections.data)))
                    # self.totalcorrections_den[chan] = total

                if chan in self.data.KG1_data.fj_dcn.keys():
                    if self.data.KG1_data.fj_dcn[chan].data is None:
                        total_dcn = 0
                    elif self.data.KG1_data.fj_dcn[chan].data.size==0:
                        total_dcn = 0
                        # self.totalcorrections_den_dcn[chan]= total_dcn
                    else:
                        total_dcn = int(round(np.sum(self.data.KG1_data.fj_dcn[chan].data)))
                        # self.totalcorrections_den_dcn[chan] = total_dcn
                else:
                    total_dcn = 0

                self.lineEdit_totcorr.setText(str(total) + ' /DCN= '+ str(total_dcn))






            if chan > 4:
                if self.data.KG1_data.density[chan].corrections.data is None:
                    total1 = 0
                elif self.data.KG1_data.density[chan].corrections.data.size==0:
                    total1 = 0
                    # self.totalcorrections_den_dcn[chan] = total1
                else:
                    total1 = int(round(np.sum(self.data.KG1_data.density[chan].corrections.data)))
                    # self.totalcorrections_den_dcn[chan] = total1
                if self.data.KG1_data.vibration[chan].corrections.data is None:
                    total2 = 0
                elif self.data.KG1_data.vibration[chan].corrections.data.size==0:
                    total2 = 0
                    # self.totalcorrections_vib_dcn[chan] = total2
                else:
                    total2 = int(round(np.sum(self.data.KG1_data.vibration[chan].corrections.data)))
                    # self.totalcorrections_vib_dcn[chan] = total2


                if chan in self.data.KG1_data.fj_dcn.keys():
                    if self.data.KG1_data.fj_dcn[chan].data is None:
                        total1_dcn = 0
                        # self.totalcorrections_den_dcn[chan] = total1_dcn
                    else:
                        total1_dcn = int(round(np.sum(self.data.KG1_data.fj_dcn[chan].data)))
                        # self.totalcorrections_den_dcn[chan] = total1_dcn
                else:
                    total1_dcn = 0

                if chan + 4 in self.data.KG1_data.fj_dcn.keys():
                    if self.data.KG1_data.fj_dcn[chan+4].data is None:
                        total2_dcn = 0
                        # self.totalcorrections_vib_dcn[chan] = total2_dcn
                    else:
                        total2_dcn = int(round(np.sum(self.data.KG1_data.fj_dcn[chan+4].data)))
                        # self.totalcorrections_vib_dcn[chan+4] = total2_dcn
                else:
                    total2_dcn = 0





                self.lineEdit_totcorr.setText(
                        str(total1) + ',' + str(total2) + ' /DCN= '+ str(total1_dcn) + ',' + str(total2_dcn))
                #
        else:
            self.lineEdit_totcorr.setEnabled(False)

    @QtCore.pyqtSlot()
    def singlecorrection(self):
        """
        this module applies single correction to selected channel

        :return:
        """

        # pyqt_set_trace()

        ax1 = self.ax1
        ax2 = self.ax2
        ax3 = self.ax3
        ax4 = self.ax4
        ax5 = self.ax5
        ax6 = self.ax6
        ax7 = self.ax7
        ax8 = self.ax8

        ax_name = 'ax' + str(self.chan)

        self.blockSignals(True) # signals emitted by this object are blocked
        self.correction_to_be_applied = self.lineEdit_mancorr.text() # reads correction from gui
        if str(self.chan).isdigit() == True:
            self.chan = int(self.chan)
            time = self.data.KG1_data.density[self.chan].time
            data = self.data.KG1_data.density[self.chan].data
            coord = self.setcoord(self.chan) # get point selected from canvas
        else:
            self.update_channel(self.chan)
            logger.info('applying this correction {} '.format(
                (self.correction_to_be_applied)))

            # self.pushButton_undo.disconnect()
            self.gettotalcorrections()
            self.pushButton_undo.clicked.connect(self.discard_single_point)
            self.kb.apply_pressed_signal.disconnect(self.singlecorrection)
            self.blockSignals(False)
            return
        if int(self.chan) <5:
            suggested_den = self.suggestcorrection() # compute correction based on fringe jump on selected point
            try:
                self.corr_den = int(self.lineEdit_mancorr.text()) * self.data.constants.DFR_DCN # convert fringe jump into density
            except ValueError: #check if self.coor_den is a number
                logger.error('use numerical values')
                self.lineEdit_mancorr.setText("")
                self.update_channel(self.chan) #update data and canvas
                logger.info('applying this correction {} '.format(
                    (self.correction_to_be_applied)))

                # self.pushButton_undo.disconnect()
                self.gettotalcorrections() # compute total correction
                self.pushButton_undo.clicked.connect(self.discard_single_point) # connect undo button to slot to undo single correction
                self.kb.apply_pressed_signal.disconnect(self.singlecorrection) # disconnect slot
                self.blockSignals(False)
                return
            if (int(suggested_den) != int(self.corr_den)):
                logger.warning('suggested correction is different, do you wish to use it?')
                ret = qm.question(self,'', "suggested correction is different: " +str(suggested_den)+"\n  Do you wish to use it?", qm.Yes | qm.No)
                # x  = input('y/n?')
                if ret==qm.Yes:
                # if x.lower() == "y":
                    self.corr_den = suggested_den
                else:
                    pass
        elif  int(self.chan) > 4:
            suggested_den, suggested_vib = self.suggestcorrection()
            try:
                self.corr_den = int(self.lineEdit_mancorr.text().split(",")[0])
                self.corr_vib = int(self.lineEdit_mancorr.text().split(",")[1])

                corrections = self.data.matrix_lat_channels.dot([self.corr_den, self.corr_vib])
                self.corr_den = corrections[0]
                self.corr_vib = corrections[1]

            except IndexError:
                logger.warning('no vibration correction')
                self.lineEdit_mancorr.setText("")
                self.update_channel(self.chan)
                logger.info('applying this correction {} '.format(
                    (self.correction_to_be_applied)))

                # self.pushButton_undo.disconnect()
                self.gettotalcorrections()
                self.pushButton_undo.clicked.connect(self.discard_single_point)
                self.kb.apply_pressed_signal.disconnect(self.singlecorrection)
                self.blockSignals(False)
                return
            except ValueError:
                logger.error('use numerical values')
                self.lineEdit_mancorr.setText("")
                self.update_channel(self.chan)
                logger.info('applying this correction {} '.format(
                    (self.correction_to_be_applied)))

                # self.pushButton_undo.disconnect()
                self.gettotalcorrections()
                self.pushButton_undo.clicked.connect(self.discard_single_point)
                self.kb.apply_pressed_signal.disconnect(self.singlecorrection)
                self.blockSignals(False)
                return
            if ((int(suggested_den) != int(self.corr_den))) & (int(suggested_vib) != int(self.corr_vib)):
                logger.warning('suggested correction is different, do you wish to use it?')
                ret = qm.question(self,'', "suggested correction is different: " +str(suggested_den)+', '+ str(suggested_vib) +"\n  Do you wish to use it?", qm.Yes | qm.No)

                # x  = input('y/n?')
                if ret==qm.Yes:
                # x  = input('y/n?')
                # if x.lower() == "y":
                    self.corr_den = suggested_den
                    self.corr_vib = suggested_vib
                else:
                    pass


        index, value = find_nearest(time, coord[0][0]) # finds nearest data point to selected point on canvas

        self.data.KG1_data.density[self.chan].correct_fj(
            self.corr_den , index=index) # correct data

        if self.data.KG1_data.density[self.chan].corrections is not None:


            xc = self.data.KG1_data.density[self.chan].corrections.time
            # for xc in xposition:


            vars()[ax_name].axvline(x=time[index], color='m', linestyle='--')
            vars()[ax_name].plot(time[index],data[index], 'mo')


        if int(self.chan) > 4:
            try:
                self.data.KG1_data.vibration[self.chan].correct_fj(
                    self.corr_vib ,
                    time=value)


            except AttributeError:
                logger.error('insert a correction for the mirror')
                self.update_channel(self.chan)
                logger.info('applying this correction {} '.format(
                    (self.correction_to_be_applied)))

                # self.pushButton_undo.disconnect()
                self.gettotalcorrections()
                self.pushButton_undo.clicked.connect(self.discard_single_point)
                self.kb.apply_pressed_signal.disconnect(self.singlecorrection)
                self.blockSignals(False)
                return
        self.update_channel(self.chan)
        logger.info('applying this correction {} '.format(
            (self.correction_to_be_applied)))

        # self.pushButton_undo.disconnect()
        self.gettotalcorrections()
        self.pushButton_undo.clicked.connect(self.discard_single_point)
        self.kb.apply_pressed_signal.disconnect(self.singlecorrection)
        self.blockSignals(False)

        logger.warning(
            'remember to mark corrections as permanent before proceeding!')

        ret = qm_permanent.question(self, '',
                          "Mark correction/s as permanent?",
                                    qm_permanent.Yes | qm_permanent.No)

        if ret == qm_permanent.Yes:

            self.handle_makepermbutton()
            self.gettotalcorrections()
        else:
            pass



    # -------------------------------.

    @QtCore.pyqtSlot()
    def get_point(self):
        """
        each tab as its own vector where input data points are stored in a list
        user later by correction modules to get where to apply corrections
        :return:
        """
        # gotcorrectionpoint = pyqtSignal()
        self.blockSignals(True)
        if self.current_tab == 'LID_1':
            self.data.coord_ch1 = [[self.widget_LID1.xs, self.widget_LID1.ys]]
            logger.debug( "Tab selected is {} - data is {} {}".format(
                self.current_tab, (self.widget_LID1.xs),
                (self.widget_LID1.ys)))
            self.widget_LID1.signal.disconnect(self.get_point)
        elif self.current_tab == 'LID_2':
            self.data.coord_ch2 = [[self.widget_LID2.xs, self.widget_LID2.ys]]
            logger.debug( "Tab selected is {} - data is {} {}".format(
                self.current_tab, (self.widget_LID2.xs),
                (self.widget_LID2.ys)))
            self.widget_LID2.signal.disconnect(self.get_point)
        elif self.current_tab == 'LID_3':
            self.data.coord_ch3 = [[self.widget_LID3.xs, self.widget_LID3.ys]]
            logger.debug( "Tab selected is {} - data is {} {}".format(
                self.current_tab, (self.widget_LID3.xs),
                (self.widget_LID3.ys)))
            self.widget_LID3.signal.disconnect(self.get_point)
        elif self.current_tab == 'LID_4':
            self.data.coord_ch4 = [[self.widget_LID4.xs, self.widget_LID4.ys]]
            logger.debug( "Tab selected is {} - data is {} {}".format(
                self.current_tab, (self.widget_LID4.xs),
                (self.widget_LID4.ys)))
            self.widget_LID4.signal.disconnect(self.get_point)
        elif self.current_tab == 'LID_5':
            self.data.coord_ch5 = [[self.widget_LID5.xs, self.widget_LID5.ys]]
            logger.debug( "Tab selected is {} - data is {} {}".format(
                self.current_tab, (self.widget_LID5.xs),
                (self.widget_LID5.ys)))
            self.widget_LID5.signal.disconnect(self.get_point)
        elif self.current_tab == 'LID_6':
            self.data.coord_ch6 = [[self.widget_LID6.xs, self.widget_LID6.ys]]
            logger.debug( "Tab selected is {} - data is {} {}".format(
                self.current_tab, (self.widget_LID6.xs),
                (self.widget_LID6.ys)))
            self.widget_LID6.signal.disconnect(self.get_point)
        elif self.current_tab == 'LID_7':
            self.data.coord_ch7 = [[self.widget_LID7.xs, self.widget_LID7.ys]]
            logger.debug( "Tab selected is {} - data is {} {}".format(
                self.current_tab, (self.widget_LID7.xs),
                (self.widget_LID7.ys)))
            self.widget_LID7.signal.disconnect(self.get_point)
        elif self.current_tab == 'LID_8':
            self.data.coord_ch8 = [[self.widget_LID8.xs, self.widget_LID8.ys]]
            logger.debug( "Tab selected is {} - data is {} {}".format(
                self.current_tab, (self.widget_LID8.xs),
                (self.widget_LID8.ys)))
            self.widget_LID8.signal.disconnect(self.get_point)
        self.blockSignals(False)

#----------------------------------
    @QtCore.pyqtSlot()
    def get_multiple_points(self):
        """
        each tab as its own vector where input data points are stored in a list
        user later by correction modules to get where to apply corrections
        :return:
        """
        # gotcorrectionpoint = pyqtSignal()
        self.blockSignals(True)
        if self.current_tab == 'LID_1':
            self.data.coord_ch1.append(
                (self.widget_LID1.xs, self.widget_LID1.ys))
            logger.debug( "Tab selected is {} - data is {} {}".format(
                self.current_tab, (self.widget_LID1.xs),
                (self.widget_LID1.ys)))

        elif self.current_tab == 'LID_2':
            self.data.coord_ch2.append(
                (self.widget_LID2.xs, self.widget_LID2.ys))
            logger.debug( "Tab selected is {} - data is {} {}".format(
                self.current_tab, (self.widget_LID2.xs),
                (self.widget_LID2.ys)))

        elif self.current_tab == 'LID_3':
            self.data.coord_ch3.append(
                (self.widget_LID3.xs, self.widget_LID3.ys))
            logger.debug( "Tab selected is {} - data is {} {}".format(
                self.current_tab, (self.widget_LID3.xs),
                (self.widget_LID3.ys)))

        elif self.current_tab == 'LID_4':
            self.data.coord_ch4.append(
                (self.widget_LID4.xs, self.widget_LID4.ys))
            logger.debug( "Tab selected is {} - data is {} {}".format(
                self.current_tab, (self.widget_LID4.xs),
                (self.widget_LID4.ys)))

        elif self.current_tab == 'LID_5':
            self.data.coord_ch5.append(
                (self.widget_LID5.xs, self.widget_LID5.ys))
            logger.debug( "Tab selected is {} - data is {} {}".format(
                self.current_tab, (self.widget_LID5.xs),
                (self.widget_LID5.ys)))

        elif self.current_tab == 'LID_6':
            self.data.coord_ch6.append(
                (self.widget_LID6.xs, self.widget_LID6.ys))
            logger.debug( "Tab selected is {} - data is {} {}".format(
                self.current_tab, (self.widget_LID6.xs),
                (self.widget_LID6.ys)))

        elif self.current_tab == 'LID_7':
            self.data.coord_ch7.append(
                (self.widget_LID7.xs, self.widget_LID7.ys))
            logger.debug( "Tab selected is {} - data is {} {}".format(
                self.current_tab, (self.widget_LID7.xs),
                (self.widget_LID7.ys)))

        elif self.current_tab == 'LID_8':
            self.data.coord_ch8.append(
                (self.widget_LID8.xs, self.widget_LID8.ys))
            logger.debug( "Tab selected is {} - data is {} {}".format(
                self.current_tab, (self.widget_LID8.xs),
                (self.widget_LID8.ys)))
        self.blockSignals(False)



    # ----------------------------------
    @QtCore.pyqtSlot()
    def discard_single_point(self):
        """
        after a single correction is applied
        this function allows the user to undo it

        before it is permanently applied
        :return:
        """
        ax1 = self.ax1
        ax2 = self.ax2
        ax3 = self.ax3
        ax4 = self.ax4
        ax5 = self.ax5
        ax6 = self.ax6
        ax7 = self.ax7
        ax8 = self.ax8

        ax_name = 'ax' + str(self.chan)

        if str(self.chan).isdigit() == True:
            chan = int(self.chan)
            time = self.data.KG1_data.density[chan].time
            data = self.data.KG1_data.density[chan].data

            coord = self.setcoord(self.chan)
            if is_empty(coord):
                logger.error(
                    'nothing to undo')
                return
            else:

                self.setcoord(self.chan,reset=True)

        else:
            return

        logger.log(5,"looking for correction at {}".format(coord[-1:][0][0]))
        index, value = find_nearest(time, coord[-1:][0][0])
        logger.info("undoing correction at {} with index {}".format(index, value))


        self.data.KG1_data.density[chan].uncorrect_fj(
            self.corr_den , index=index)

        if int(self.chan) > 4:
            vibration = SignalBase(self.data.constants)
            vibration = self.data.KG1_data.vibration[chan]

            vibration.uncorrect_fj(
                self.corr_vib , index=index)


        tstep = np.mean(np.diff(self.data.KG1_data.density[chan].time))
        linestoberemoved=[]

        for i, line in enumerate(vars()[ax_name].lines):
            logger.log(5, "checking line {} @ {}".format(i,line.get_xydata()[0][0]))
            if abs(line.get_xydata()[0][0] - value)<tstep:
                    logger.log(5, " removing line @ {}s".format(value))
                    linestoberemoved.append(i)
        for x in reversed(linestoberemoved):
            del vars()[ax_name].lines[x]





        # if self.chan == 1:
        #     del self.ax1.lines[-num_of_correction:]
        #
        # elif self.chan == 2:
        #     del self.ax2.lines[-num_of_correction:]
        #
        # elif self.chan == 3:
        #     del self.ax3.lines[-num_of_correction:]
        #
        # elif self.chan == 4:
        #     del self.ax4.lines[-num_of_correction:]
        #
        # elif self.chan == 5:
        #     del self.ax5.lines[-num_of_correction:]
        #
        # elif self.chan == 6:
        #     del self.ax6.lines[-num_of_correction:]
        #
        # elif self.chan == 7:
        #     del self.ax7.lines[-num_of_correction:]
        #
        # elif self.chan == 8:
        #     del self.ax8.lines[-num_of_correction:]

        self.update_channel(int(self.chan))
        self.gettotalcorrections()
        self.pushButton_undo.clicked.disconnect(self.discard_single_point)

        # -----------------------------------------------
    @QtCore.pyqtSlot()
    def discard_neutralise_corrections(self):
            """
            after correction are neutralised
            this function allows the user to undo it

            before it is permanently applied

            :return:
            """
            ax1 = self.ax1
            ax2 = self.ax2
            ax3 = self.ax3
            ax4 = self.ax4
            ax5 = self.ax5
            ax6 = self.ax6
            ax7 = self.ax7
            ax8 = self.ax8
            
            if str(self.chan).isdigit() == True:
                chan = int(self.chan)
                time = self.data.KG1_data.density[chan].time
                data = self.data.KG1_data.density[chan].data

                coord = self.setcoord(self.chan)
                if is_empty(coord):
                    logger.error(
                        "no data points collected from canvas, nothing to undo")
                    self.update_channel(self.chan)
                    self.gettotalcorrections()
                    self.pushButton_undo.clicked.connect(self.discard_neutralise_corrections)
                    self.kb.apply_pressed_signal.disconnect(self.neutralisatecorrections)
                    self.disconnnet_neutralisepointswidget()

                    self.blockSignals(False)
                    return
                else:

                    self.setcoord(self.chan, reset=True)
            else:
                self.update_channel(self.chan)
                self.gettotalcorrections()
                self.pushButton_undo.clicked.connect(
                    self.discard_neutralise_corrections)
                self.kb.apply_pressed_signal.disconnect(
                    self.neutralisatecorrections)
                self.disconnnet_neutralisepointswidget()

                self.blockSignals(False)

                return
            # try:
            min_coord = min(coord)
            max_coord = max(coord)
            indexes, values = find_within_range(self.data.KG1_data.density[self.chan].corrections.time,min_coord[0],max_coord[0])
            indexes_automatic, values_automatic = find_within_range(
                self.data.KG1_data.fj_dcn[self.chan].time, min_coord[0],
                max_coord[0])
            #unique values
            # values = list(set(values)) # using this insctruction creates an error
            # as creates a mismatch between times of correction and value of the correction
            # even thought it is the best way to avoid duplicates
            corrections = self.data.KG1_data.density[self.chan].corrections.data[indexes]
            if int(self.chan) > 4:
                corrections_vib = \
                self.data.KG1_data.vibration[self.chan].corrections.data[indexes]
            for i, value in enumerate(values):

                index, value = find_nearest(time, value)

                self.corr_den = int(round(corrections[i]))
                time_corr =  values[i]


                logger.info("undoing correction @t= {}".format(str(time_corr)))


                if int(self.chan) > 4:
                    # logging.warning('assuming mirror correction = 0 !')

                    self.corr_vib = int(round(corrections_vib[i]))

                    M = self.data.matrix_lat_channels

                    correction_to_be_restored = M.dot(np.array([self.corr_den,self.corr_vib]))  # get suggested correction by solving linear problem Ax=b

                    restored_den = correction_to_be_restored[0]
                    restored_vib = correction_to_be_restored[1]

                    # lid = neutralised_correction[0]
                    # mir = neutralised_correction[1]

                    self.data.KG1_data.density[chan].uncorrect_fj(self.corr_den,
                        index=index,fringe_vib = restored_den)


                    self.data.KG1_data.vibration[
                            self.chan].uncorrect_fj(self.corr_vib,
                            index=index,fringe_vib=restored_vib)
                else:

                    self.data.KG1_data.density[chan].uncorrect_fj(
                        self.corr_den * self.data.constants.DFR_DCN,
                        index=index)

                    # if self.data.KG1_data.density[self.chan].corrections is not None:
                ax_name = 'ax' + str(self.chan)

                vars()[ax_name].axvline(x=time_corr, color='y',
                                            linestyle='--')

            self.update_channel(int(self.chan))



            self.gettotalcorrections()
            self.pushButton_undo.clicked.disconnect(self.discard_neutralise_corrections)

    # -----------------------------------------------
    @QtCore.pyqtSlot()
    def discard_multiple_points(self):
        """
        after multiple corrections are applied
        this function allows the user to undo it

        before it are permanently applied

        :return:
        """

        ax1 = self.ax1
        ax2 = self.ax2
        ax3 = self.ax3
        ax4 = self.ax4
        ax5 = self.ax5
        ax6 = self.ax6
        ax7 = self.ax7
        ax8 = self.ax8

        ax_name = 'ax' + str(self.chan)

        if str(self.chan).isdigit() == True:
            chan = int(self.chan)
            time = self.data.KG1_data.density[chan].time
            data = self.data.KG1_data.density[chan].data

            coord = self.setcoord(self.chan)
            if is_empty(coord):
                logger.error(
                    "nothing to undo")
                return
            else:

                self.setcoord(self.chan,reset=True)
        else:
            return
        # try:

        for i, value in enumerate(coord):
            logger.info("undoing correction @t= {}".format(str(value[0])))
            index, value = find_nearest(time, value[0])
            logger.log(5, " found point to undo at {} with index {}".format(index, value))

            self.data.KG1_data.density[chan].uncorrect_fj(
                self.corr_den , index=index)

            if int(self.chan) > 4:
                vibration = SignalBase(self.data.constants)
                vibration = self.data.KG1_data.vibration[chan]

                vibration.uncorrect_fj(
                    self.corr_vib , index=index)
        #
        tstep = np.mean(np.diff(self.data.KG1_data.density[chan].time))
        linestoberemoved=[]
        for j, value in enumerate(coord):
            for i, line in enumerate(vars()[ax_name].lines):
                logger.log(5, "checking line {} @ {}".format(i,line.get_xydata()[0][0]))
                if abs(line.get_xydata()[0][0] - value[0])<tstep:
                        logger.log(5, " removing line @ {}s".format(value))
                        linestoberemoved.append(i)
        for x in reversed(linestoberemoved):
            del vars()[ax_name].lines[x]


        self.update_channel(int(self.chan))
        self.gettotalcorrections()
        self.pushButton_undo.clicked.disconnect(self.discard_multiple_points)

#--------------------------
    def which_tab(self):
        """
        function used to detect which tab is currently active and set ax and widget

        :return: ax and widget name of current tab
        """
        if int(self.chan) == 1:
            ax = self.ax1
            widget = self.widget_LID1
        elif int(self.chan) == 2:
            ax = self.ax2
            widget = self.widget_LID2
        elif int(self.chan) == 3:
            ax = self.ax3
            widget = self.widget_LID3
        elif int(self.chan) == 4:
            ax = self.ax4
            widget = self.widget_LID4
        elif int(self.chan) == 5:
            ax = self.ax5
            widget = self.widget_LID5
        elif int(self.chan) == 6:
            ax = self.ax6
            widget = self.widget_LID6
        elif int(self.chan) == 7:
            ax = self.ax7
            widget = self.widget_LID7
        elif int(self.chan) == 8:
            ax = self.ax8
            widget = self.widget_LID8
        return ax, widget

    # -------------------------------
    def show_kb(self):
        """
        function that shows or hide the widget used to select corrections
        so far max/min correction are +/- 5 fringes
        :return:
        """
        if self.kb.isHidden():
            self.kb.show()
        else:
            self.kb.hide()

    # ----------------------------
    @QtCore.pyqtSlot()
    def handle_exit_button(self):
        """
        Exit the application
        """
        if hasattr(self.data, 'pulse') is False:
            logger.debug( 'data has been loaded, nothing has been modified, it is save to exit')

            self.areyousure_window = QtGui.QMainWindow()
            self.ui_areyousure = Ui_areyousure_window()
            self.ui_areyousure.setupUi(self.areyousure_window)
            self.areyousure_window.show()

            self.ui_areyousure.pushButton_YES.clicked.connect(
                self.handle_yes_exit)
            self.ui_areyousure.pushButton_NO.clicked.connect(
                self.handle_no)
        elif self.data.pulse is None:
            logger.debug('no data has been loaded, it is save to exit')

            self.areyousure_window = QtGui.QMainWindow()
            self.ui_areyousure = Ui_areyousure_window()
            self.ui_areyousure.setupUi(self.areyousure_window)
            self.areyousure_window.show()

            self.ui_areyousure.pushButton_YES.clicked.connect(
                self.handle_yes_exit)
            self.ui_areyousure.pushButton_NO.clicked.connect(
                self.handle_no)

            #logger.info(' Exit now')
            #sys.exit()
        elif hasattr(self.data, 'KG1_data') is False:
            logger.debug('no data has been loaded, it is save to exit')

            self.areyousure_window = QtGui.QMainWindow()
            self.ui_areyousure = Ui_areyousure_window()
            self.ui_areyousure.setupUi(self.areyousure_window)
            self.areyousure_window.show()

            self.ui_areyousure.pushButton_YES.clicked.connect(
                self.handle_yes_exit)
            self.ui_areyousure.pushButton_NO.clicked.connect(
                self.handle_no)

        elif (self.data.data_changed | self.data.statusflag_changed) is True:
            logger.debug( "data changed? {} status flags changed? {}".format(self.data.data_changed, self.data.statusflag_changed))
            if self.data.saved:
                logger.debug("data has been saved")
                self.handle_yes_exit()
            else:
                logger.info(' data has not been saved do you want to exit? ')

                self.areyousure_window = QtGui.QMainWindow()
                self.ui_areyousure = Ui_areyousure_window()
                self.ui_areyousure.setupUi(self.areyousure_window)
                self.areyousure_window.show()

                self.ui_areyousure.pushButton_YES.clicked.connect(
                    self.handle_yes_exit)
                self.ui_areyousure.pushButton_NO.clicked.connect(
                    self.handle_no)
        else:
            logger.info('data and status flags have not changed, it is save to exit')


            self.areyousure_window = QtGui.QMainWindow()
            self.ui_areyousure = Ui_areyousure_window()
            self.ui_areyousure.setupUi(self.areyousure_window)
            self.areyousure_window.show()

            self.ui_areyousure.pushButton_YES.clicked.connect(
                self.handle_yes_exit)
            self.ui_areyousure.pushButton_NO.clicked.connect(
                self.handle_no)
    #except AttributeError:
        #logger.info('')
        #logger.info('Exit now')
        #sys.exit()

    @staticmethod
    def handle_yes_exit():
        """
        close application
        ::todo: check why using this function doens't allow to use profiling (what exit values does it need?)
        """

        #logger.info('')
        logger.info(' Exit now')
        QtCore.QCoreApplication.instance().quit()
        # sys.exit()







def main():
    """
    Main function

    the only input to the GUI is the debug

    by default is set to INFO
    """
    from PyQt4.QtCore import pyqtRemoveInputHook
    pyqtRemoveInputHook()
    pr = cProfile.Profile()
    pr.enable()

    # with PyCallGraph(output=GraphvizOutput()):
        # code_to_profile()

    app = QtGui.QApplication(sys.argv)
    # screen_resolution = app.desktop().screenGeometry()
    # width, height = screen_resolution.width(), screen_resolution.height()
    width, height = [640,480]
    width, height = [480,360]
    MainWindow = CORMAT_GUI()
    screenShape = QtGui.QDesktopWidget().screenGeometry()
    logger.debug( 'screen resolution is {} x {}'.format(screenShape.width(), screenShape.height()))
    # 1366x768 vnc viewer size
    # time.sleep(3.0)
    MainWindow.show()
    # MainWindow.resize(screenShape.width(), screenShape.height())
    MainWindow.resize(width, height)
    # MainWindow.showMaximized()
    app.exec_()
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)

    ps.dump_stats('stats.dmp')  # dump the stats to a file named stats.dmp
    # ps.print_stats(sort='time')
    return

if __name__ == '__main__':


    # Ensure we are running on 64bit
    assert (platform.architecture()[0] == '64bit'), "Please log on Freja"

    # Ensure we are running python 3
    assert sys.version_info >= (
        3, 5), "Python version too old. Please use >= 3.5.X."

    parser = argparse.ArgumentParser(description='Run CORMAT_py')
    parser.add_argument("-d", "--debug", type=int,
                        help="Debug level. 0: Info, 1: Warning, 2: Debug,"
                             " 3: Error, 4: Debug Plus; \n default level is INFO", default=4)
    parser.add_argument("-doc", "--documentation", type=str,
                        help="Make documentation. yes/no", default='no')

    args = parser.parse_args(sys.argv[1:])


    debug_map = {0: logging.INFO,
                 1: logging.WARNING,
                 2: logging.DEBUG,
                 3: logging.ERROR,
                 4: 5}
    #this plots logger twice (black plus coloured)
    logging.addLevelName(5, "DEBUG_PLUS")
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=debug_map[args.debug])
    # logger.setLevel(debug_map[args.debug])

    fmt = MyFormatter()
    # hdlr = logging.StreamHandler(sys.stdout)


    # hdlr.setFormatter(fmt)
    # logging.root.addHandler(hdlr)
    fh = handlers.RotatingFileHandler('./LOGFILE.DAT', mode = 'w',maxBytes=(1048576*5), backupCount=7)
    fh.setFormatter(fmt)
    logging.root.addHandler(fh)





    main()


    

    
