#!/usr/bin/env python
"""
Class that runs CORMAT_py GUI
"""


# ----------------------------
__author__ = "Bruno Viola"
__Name__ = "CORMAT_py"
__version__ = "0.1"
__release__ = "0"
__maintainer__ = "Bruno Viola"
__email__ = "bruno.viola@ukaea.uk"
__status__ = "Testing"
# __status__ = "Production"
__credits__ = ["aboboc"]

import argparse
import logging
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
from areyousure_gui import Ui_areyousure_window
#  pdb.set_trace()
from consts import Consts
from elms_data import ElmsData
from find_disruption import find_disruption
from hrts_data import HRTSData
# from kg1_data import Kg1Data
from kg1_ppf_data import Kg1PPFData
from kg4_data import Kg4Data
# import library containing useful function
from library import *
from lidar_data import LIDARData
# from kg1_consts import Kg1Consts
from mag_data import MagData
from matplotlib import gridspec
from matplotlib.backends.backend_qt4agg import \
    NavigationToolbar2QT as NavigationToolbar
from nbi_data import NBIData
from pellet_data import PelletData
from ppf import *
from ppf_write import *
from signal_base import SignalBase
from pdb import set_trace as bp


plt.rcParams["savefig.directory"] = os.chdir(os.getcwd())
from custom_formatters import MyFormatter,QPlainTextEditLogger,HTMLFormatter
logger = logging.getLogger(__name__)

import inspect
myself = lambda: inspect.stack()[1][3]
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
        :param widget:
        :return:
        """

        # widget.figure.clear()
        # widget.draw()

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


        """

        import os
        super(CORMAT_GUI, self).__init__(parent)
        self.setupUi(self)
        self.data = lambda: None
        
        # -------------------------------
        ###setting up the logger to write inside a Text box
        # -------------------------------
        logTextBox = QPlainTextEditLogger(self)
        # You can format what is printed to text box
        #logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        #logTextBox.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

        logTextBox.setFormatter(HTMLFormatter())
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        # logging.getLogger().setLevel(logging.INFO)

        # -------------------------------
        # initialising new pulse checkbox to false
        # -------------------------------
        self.checkBox_newpulse.setChecked(False)

        # -------------------------------
        #old pulse contains information on the last pulse analysed
        self.data.old_pulse = None
        #pulse is the current pulse
        self.data.pulse = None

        # -------------------------------
        #initialisation of control variables
        # -------------------------------
        # set saved status to False
        
        self.data.saved = False
        self.data.data_changed = False
        self.data.statusflag_changed = False
        logger.log(5, "\n {} - saved is {} - data changed is {} - status flags changed is {}".format(myself(),self.data.saved,self.data.data_changed, self.data.statusflag_changed))

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
        logger.info('\n\n\nStart CORMATpy')
        logger.info('\n\t {}'.format(datetime.datetime.today().strftime('%Y-%m-%d')))


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
        logging.info('copying to local user profile')

        logger.log(5, 'we are in %s', cwd)

        # -------------------------------
        # Read  config data.
        # -------------------------------
        logger.info(" Reading in constants.")
        try:
            self.data.constants = Consts("consts.ini", __version__)
            # constants = Kg1Consts("kg1_consts.ini", __version__)
        except KeyError:
            logger.error(" Could not read in configuration file consts.ini")
            sys.exit(65)
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
            logging.info(
                'user {} authorised to write public PPF'.format(self.owner))
            write_uis.insert(0, 'JETPPF')  # jetppf first in the combobox list
            write_uis.append(self.owner)
            # users.append('chain1')
        else:
            logging.info(
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
                           'KG1_RT']
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
        self.button_read_pulse.clicked.connect(self.handle_readbutton)
        self.button_saveppf.clicked.connect(self.handle_saveppfbutton)
        self.button_save.clicked.connect(self.dump_kg1)

        self.button_normalize.clicked.connect(self.handle_normalizebutton)
        self.button_restore.clicked.connect(self.handle_button_restore)

        self.pushButton_apply.clicked.connect(self.handle_applybutton)
        self.pushButton_makeperm.clicked.connect(self.handle_makepermbutton)
        self.pushButton_undo.clicked.connect(self.handle_undobutton)

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
        self.pushButton_apply.setEnabled(False)
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
        # self.tabWidget.setTabEnabled(0, False)
        # self.tabWidget.setTabEnabled(1, False)
        # self.tabWidget.setTabEnabled(2, False)
        # self.tabWidget.setTabEnabled(3, False)
        # self.tabWidget.setTabEnabled(4, False)
        # self.tabWidget.setTabEnabled(5, False)
        # self.tabWidget.setTabEnabled(6, False)
        # self.tabWidget.setTabEnabled(7, False)
        # self.tabWidget.setTabEnabled(8, False)
        # self.tabWidget.setTabEnabled(9, False)
        # self.tabWidget.setTabEnabled(10, False)
        # self.tabWidget.setTabEnabled(11, False)



        # -------------------------------
        # making documentation
        # -------------------------------
        if (args.documentation).lower() == 'yes':
            logging.info('\n creating documentation')

            os.chdir('../docs')
            import subprocess
            subprocess.check_output('make html', shell=True)
            subprocess.check_output('make latex', shell=True)

            os.chdir(self.home)


        # -------------------------------
        logging.info('\nINIT DONE')




#-------------------------------

    def handle_readbutton(self):
        """
        implemets what happen when clicking the load button on the GUI
        the logic is explained in the FLowDiagram ../FlowDiagram/load_button_new.dia
        """

        # -------------------------------
        # reading pulse from GUI
        # -------------------------------
        self.data.pulse = self.lineEdit_jpn.text()


        if self.data.pulse is '': #user has not entered a pulse number
            logging.error('PLEASE USE JPN < {}'.format(int(pdmsht())))
            assert self.data.pulse is not '', "ERROR no pulse selected"

            pass
        else:
            #self.data.pulse = int(self.lineEdit_jpn.text())
            try:
                int(self.data.pulse)

            except ValueError:
                #logging.error('PLEASE USE JPN < {}'.format(int(pdmsht())))
                raise SystemExit('ERROR - PLEASE USE JPN < {}'.format(int(pdmsht())))

            if int(self.data.pulse) < pdmsht():
                   pass # user has entered a valid pulse number
            else:
                logging.error('PLEASE USE JPN < {}'.format(int(pdmsht())))
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

        #
        # self.tabWidget.setTabEnabled(0, True)
        # self.tabWidget.setTabEnabled(1, True)
        # self.tabWidget.setTabEnabled(2, True)
        # self.tabWidget.setTabEnabled(3, True)
        # self.tabWidget.setTabEnabled(4, True)
        # self.tabWidget.setTabEnabled(5, True)
        # self.tabWidget.setTabEnabled(6, True)
        # self.tabWidget.setTabEnabled(7, True)
        # self.tabWidget.setTabEnabled(8, True)
        # self.tabWidget.setTabEnabled(9, True)
        # self.tabWidget.setTabEnabled(10, True)
        # self.tabWidget.setTabEnabled(11, True)

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


        # -------------------------------
        # backup for kg1 data
        self.kg1_original = {}
        # -------------------------------
        # store normalised kg1?
        self.data.kg1_norm = {}





        logger.log(1,'\n')
        # -------------------------------
        # check if kg1 is stored in workspace
        # -------------------------------
        exists = os.path.isfile('./scratch/kg1_data.pkl')

        if exists :
            assert(exists)
            logger.info( "\n The workspace contains data not saved")
            self.data.data_changed = True
            self.data.statusflag_changed = True
            self.data.saved = False

        else:
            pass



        # data_changed = equalsFile('./saved/' + str(self.data.pulse) + '_kg1.pkl',
        #                           './scratch/' + str(self.data.pulse) + '_kg1.pkl')

        if self.data.data_changed | self.data.statusflag_changed == True: # data has changed
            logger.log(5,"\n data or status flags have changed")

            if self.data.saved:  # data saved to ppf
                logger.log(5, "\n  data or status flag have been saved to PPF")
                if (self.checkBox_newpulse.isChecked()):
                    logger.log(5, '{} is  checked'.format(self.checkBox_newpulse.objectName()))

                    # -------------------------------
                    # READ data.
                    # -------------------------------
                    self.read_uid = str(self.comboBox_readuid.currentText())
                    logger.info("Reading data for pulse {}".format(str(self.data.pulse)))
                    logger.info('reading data with uid -  {}'.format((str(self.read_uid))))
                    success = self.readdata()
                    # self.tabWidget.setCurrentIndex(0)
                    # self.tabSelected(arg=0)
                    # -------------------------------
                    # PLOT KG1 data.
                    # -------------------------------
                    if success:
                        self.plot_data()

                        # -------------------------------
                        # update GUI after plot
                        # -------------------------------

                        self.update_GUI()

                        self.data.old_pulse = self.data.pulse
                    else:
                        logger.error("ERROR reading data")


                else:
                    logging.warning('\n NO action performed \t')
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
                    #logging.info('\n pulse data already downloaded - you are requesting to download again')
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
                    # logging.disable(logging.info)
                    logging.getLogger().disabled = True

                    self.load_pickle()
                    # logging.disable(logging.NOTSET)
                    logging.getLogger().disabled = False
                    logger.log(5,'checking pulse data in workspace')
                    # pyqt_set_trace()

                    self.data.old_pulse = self.data.pulse

                    self.data.pulse = int(self.lineEdit_jpn.text())
                    # pyqt_set_trace()
                    list_attr=['KG1_data','KG4_data', 'MAG_data', 'PELLETS_data','ELM_data', 'HRTS_data','NBI_data', 'is_dis', 'dis_time','LIDAR_data']
                    for attr in list_attr:
                        # pyqt_set_trace()
                        if hasattr(self, attr):
                            delattr(self,attr)
                    # pyqt_set_trace()

                    # if (self.data.old_pulse is None) | (self.data.old_pulse == self.data.pulse):
                    if  (self.data.old_pulse == self.data.pulse):
                        # -------------------------------
                        # READ data.
                        # -------------------------------
                        self.read_uid = str(self.comboBox_readuid.currentText())
                        logging.info('reading data with uid -  {}'.format(
                                (str(self.read_uid))))
                        self.load_pickle()
                        # self.tabWidget.setCurrentIndex(0)
                        # self.tabSelected(arg=0)
                        # -------------------------------
                        # PLOT KG1 data.
                        # -------------------------------

                        self.plot_data()

                            # -------------------------------
                            # update GUI after plot
                            # -------------------------------

                        self.update_GUI()

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
                #logging.info('\n pulse data already downloaded - you are requesting to download again')
                self.areyousure_window = QtGui.QMainWindow()
                self.ui_areyousure = Ui_areyousure_window()
                self.ui_areyousure.setupUi(self.areyousure_window)
                self.areyousure_window.show()

                self.ui_areyousure.pushButton_YES.clicked.connect(
                    self.handle_yes)
                self.ui_areyousure.pushButton_NO.clicked.connect(self.handle_no)
            else:
                logger.log(5, '{} is NOT checked'.format(self.checkBox_newpulse.objectName()))
                logging.error('\n no action performed')



        #now set
        self.data.saved = False
        self.data.statusflag_changed = False
        self.data.data_changed = False
        logger.log(5, "\n {} - saved is {} - data changed is {} - status flags changed is {}".format(myself(),self.data.saved,self.data.data_changed, self.data.statusflag_changed))
# ----------------------------


# -------------------------
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

        logging.info('%s has the following SF %s', str(self.data.pulse),
                     self.data.SF_list)

# ------------------------



# ------------------------
    def tabSelected(self, arg=None):
        """
        function that convert arg number into tab name
        it also sets the SF value when changing tabs
        :param arg:
        :return:
        """
        logger.log(5, 'tab number is {}'.format(str(arg + 1)))
        if arg == 0:
            logger.log(5, 'status flag is {}'.format(str(self.data.SF_ch1)))
            self.groupBox_statusflag.setEnabled(True)
            self.current_tab = 'LID_1'
            self.set_status_flag_radio(int(self.data.SF_ch1))
        if arg == 1:
            logger.log(5, 'status flag is {}'.format(str(self.data.SF_ch2)))
            self.groupBox_statusflag.setEnabled(True)
            self.current_tab = 'LID_2'
            self.set_status_flag_radio(int(self.data.SF_ch2))
        if arg == 2:
            logger.log(5, 'status flag is {}'.format(str(self.data.SF_ch3)))
            self.groupBox_statusflag.setEnabled(True)
            self.current_tab = 'LID_3'
            self.set_status_flag_radio(int(self.data.SF_ch3))
        if arg == 3:
            logger.log(5, 'status flag is {}'.format(str(self.data.SF_ch4)))
            self.groupBox_statusflag.setEnabled(True)
            self.current_tab = 'LID_4'
            self.set_status_flag_radio(int(self.data.SF_ch4))
        if arg == 4:
            logger.log(5, 'status flag is {}'.format(str(self.data.SF_ch5)))
            self.groupBox_statusflag.setEnabled(True)
            self.current_tab = 'LID_5'
            self.set_status_flag_radio(int(self.data.SF_ch5))
        if arg == 5:
            logger.log(5, 'status flag is {}'.format(str(self.data.SF_ch6)))
            self.groupBox_statusflag.setEnabled(True)
            self.current_tab = 'LID_6'
            self.set_status_flag_radio(int(self.data.SF_ch6))
        if arg == 6:
            logger.log(5, 'status flag is {}'.format(str(self.data.SF_ch7)))
            self.groupBox_statusflag.setEnabled(True)
            self.current_tab = 'LID_7'
            self.set_status_flag_radio(int(self.data.SF_ch7))
        if arg == 7:
            logger.log(5, 'status flag is {}'.format(str(self.data.SF_ch8)))
            self.groupBox_statusflag.setEnabled(True)
            self.current_tab = 'LID_8'
            self.set_status_flag_radio(int(self.data.SF_ch8))
        if arg == 8:
            self.groupBox_statusflag.setEnabled(False)
            self.current_tab = 'LID_1-4'
        if arg == 9:
            self.groupBox_statusflag.setEnabled(False)
            self.current_tab = 'LID_5-8'
        if arg == 10:
            self.groupBox_statusflag.setEnabled(False)
            self.current_tab = 'LID_ALL'
        if arg == 11:
            self.groupBox_statusflag.setEnabled(False)
            self.current_tab = 'MIR'

        logger.log(5, '\n\t: current Tab is {}'.format(self.current_tab))

# -------------------------
    def checkstate(self, button):

        """
        connect tab number to LID channel and sets status flag
        it also performs a check if the user clicked a radio button to change status flag for current tab/channel
        :param button:
        :return:
        """
        snd = self.sender() # gets object that called


        SF = snd.objectName().split('_')[2]  # statusflag value selected

        # logger.log(5, '{} has status flag {}'.format(self.current_tab,str(SF_old)))

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


        if (int(self.data.SF_old1) != int(self.data.SF_ch1)):

            self.data.statusflag_changed = True
            logger.log(5, "status flag LID1 changed by user")

        elif (int(self.data.SF_old2) != int(self.data.SF_ch2)):

            self.data.statusflag_changed = True
            logger.log(5, "status flag LID2 changed by user")

        elif (int(self.data.SF_old3) != int(self.data.SF_ch3)):

            self.data.statusflag_changed = True
            logger.log(5, "status flag LID3 changed by user")

        elif (int(self.data.SF_old4) != int(self.data.SF_ch4)):

            self.data.statusflag_changed = True
            logger.log(5, "status flag LID4 changed by user")

        elif (int(self.data.SF_old5) != int(self.data.SF_ch5)):

            self.data.statusflag_changed = True
            logger.log(5, "status flag LID5 changed by user")

        elif (int(self.data.SF_old6) != int(self.data.SF_ch6)):

            self.data.statusflag_changed = True
            logger.log(5, "status flag LID6 changed by user")

        elif (int(self.data.SF_old7) != int(self.data.SF_ch7)):

            self.data.statusflag_changed = True
            logger.log(5, "status flag LID7 changed by user")

        elif (int(self.data.SF_old8) != int(self.data.SF_ch8)):

            self.data.statusflag_changed = True
            logger.log(5, "status flag LID8 changed by user")






        # logger.log(5, '{} new status flag is {}'.format(self.current_tab, str(SF)))

        # print(snd.objectName(),SF)
        # if SF == 0:

        # self.set_status_flag_radio(SF)
        #
        # self.current_tab
        # self.ui_plotdata.checkBox.setChecked(False)


# -------------------------

    def set_status_flag_radio(self, value):
        """
        converts status flag integer value into boolean to check SF radio buttons in GUI
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




            # do not change this flag after reading data_changed


        logger.log(5, 'data saved is {} - status flag saved is - data changed is {}'.format(self.data.saved,self.data.statusflag_changed, self.data.data_changed))


    # ------------------------
    def load_pickle(self):
        """
        loads last saved data from non saved operations
        data are saved in pickle format (binary)

        also to be used when reloading a pulse
        """
        logging.info('\n loading pulse data from workspace')
        # Python 3: open(..., 'rb')
        with open('./saved/data.pkl',
                  'rb') as f:
            [self.data.pulse, self.data.KG1_data,
             self.data.KG4_data, self.data.MAG_data, self.data.PELLETS_data,
             self.data.ELM_data, self.data.HRTS_data,
             self.data.NBI_data, self.data.is_dis, self.data.dis_time,
             self.data.LIDAR_data] = pickle.load(f)
        f.close()
        with open('./saved/kg1_data.pkl',
                  'rb') as f:  # Python 3: open(..., 'rb')
            [self.data.KG1_data, self.data.SF_list, self.data.unval_seq, self.data.val_seq,
             self.read_uid] = pickle.load(f)
        f.close()
        logging.info('\n workspace loaded')
        logging.info(
            '\n workspace data comes from userid {}'.format(self.read_uid))
        logging.info(
            '{} has the following SF {}'.format(str(self.data.pulse), self.data.SF_list))
        if self.data.KG1_data.mode != "Automatic Corrections":
            self.data.KG1_data.correctedby = self.data.KG1_data.mode.split(" ")[2]
            logging.info('{} last validated seq is {} by {}'.format(str(self.data.pulse),
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

    # ------------------------
    def save_to_pickle(self,folder):
        logging.info('\n saving pulse data')
        with open('./' + folder + 'data.pkl', 'wb') as f:
            pickle.dump(
                [self.data.pulse, self.data.KG1_data,
                 self.data.KG4_data, self.data.MAG_data, self.data.PELLETS_data,
                 self.data.ELM_data, self.data.HRTS_data,
                 self.data.NBI_data, self.data.is_dis, self.data.dis_time,
                 self.data.LIDAR_data], f)
        f.close()
        logging.info('\n data saved')

    # ------------------------
    def save_kg1(self,folder):
        logging.info('\n saving KG1 data')
        with open('./' + folder + '/kg1_data.pkl', 'wb') as f:
            pickle.dump(
                [self.data.KG1_data, self.data.SF_list, self.data.unval_seq, self.data.val_seq,
                 self.read_uid], f)
        f.close()
        logging.info('\n KG1 data saved')



    def dump_kg1(self):
        logging.info('\n saving KG1 data')
        self.save_kg1('scratch')
        logging.info('\n KG1 data saved')
        #logging.info('\n saving changes to KG1 data')
        #with open('./scratch/kg1_data.pkl', 'wb') as f:
            #pickle.dump(
                #[self.data.KG1_data, self.data.SF_list, self.data.unval_seq, self.data.val_seq,
                 #self.read_uid,self.data.data_changed,self.data.statusflag_changed,self.data.saved], f)
        #f.close()
        #logging.info('\n scratch KG1 data saved')

#----------------------------



    def handle_no(self):
        """
        functions that ask to confirm if user wants NOT to proceed

        to set read data for selected pulse
    """

        # button_name = button.objectName()
        # print(button_name)


        logger.log(5, 'pressed %s button',
                      self.ui_areyousure.pushButton_NO.text())
        logging.info('go back and perform a different action')

        self.ui_areyousure.pushButton_NO.setChecked(False)

        self.areyousure_window.hide()

    # ----------------------------
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

            # define now two gridspecs
            # gs is the gridspec per channels 1-4
            # gs1 is the gridspec for channels 5-8
            # when plotting markers they will allocate space to plot markers in a subplot under current plot

            # gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])# working: creates canvas with 2 columns in the ratio 1/3

            self.plot_data()

            self.update_GUI()

            self.data.old_pulse = self.data.pulse

            # now set
            logger.log(5, "\n {} - saved is {} - data changed is {} - status flags changed is {}".format(myself(),self.data.saved,self.data.data_changed, self.data.statusflag_changed))
        else:
            logger.error("ERROR reading data")
    # -----------------------
    def handle_yes_reload(self):

        logging.info('\n pulse data already downloaded')
        self.load_pickle()
        # self.tabWidget.setCurrentIndex(0)
        # self.tabSelected(arg=0)

        # -------------------------------
        # PLOT KG1 data.
        # -------------------------------

        self.plot_data()

        # -------------------------------
        # update GUI after plot
        # -------------------------------

        self.update_GUI()
        #

        self.data.old_pulse = self.data.pulse
        logger.log(5, 'old pulse is {}, new pulse is {}'.format(self.data.old_pulse, self.data.pulse))
        # now set
        self.data.saved = False
        self.data.statusflag_changed = False
        self.data.data_changed = False
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
        MAG_data = MagData(self.data.constants)
        success = MAG_data.read_data(self.data.pulse)
        if not success:
            logging.error(
                'no MAG data for pulse {} with uid {}'.format(self.data.pulse,
                                                               self.read_uid))
        self.data.MAG_data = MAG_data

        # -------------------------------
        # 2. Read in KG1 data
        # -------------------------------
        logger.info("             Reading in KG1 data.")
        KG1_data = Kg1PPFData(self.data.constants,self.data.pulse)
        self.data.KG1_data = KG1_data

        self.read_uid = self.comboBox_readuid.currentText()
        success = KG1_data.read_data(self.data.pulse, read_uid=self.read_uid)

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
        KG4_data = Kg4Data(self.data.constants)
        KG4_data.read_data(self.data.MAG_data, self.data.pulse)
        self.data.KG4_data = KG4_data
        # pdb.set_trace()

        # -------------------------------
        # 5. Read in pellet signals
        # -------------------------------
        logger.info("             Reading in pellet data.")
        PELLETS_data = PelletData(self.data.constants)
        PELLETS_data.read_data(self.data.pulse)
        self.data.PELLETS_data = PELLETS_data
        # -------------------------------
        # 6. Read in NBI data.
        # -------------------------------
        logger.info("             Reading in NBI data.")
        NBI_data = NBIData(self.data.constants)
        NBI_data.read_data(self.data.pulse)
        self.data.NBI_data = NBI_data
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
        ELM_data = ElmsData(self.data.constants, self.data.pulse, dis_time=dis_time[0])
        self.data.ELM_data = ELM_data
        # -------------------------------
        # 9. Read HRTS data
        # # -------------------------------
        logger.info("             Reading in HRTS data.")
        HRTS_data = HRTSData(self.data.constants)
        HRTS_data.read_data(self.data.pulse)
        self.data.HRTS_data = HRTS_data
        # # # # -------------------------------
        # # # 10. Read LIDAR data
        # # # -------------------------------
        logger.info("             Reading in LIDAR data.")
        LIDAR_data = LIDARData(self.data.constants)
        LIDAR_data.read_data(self.data.pulse)
        self.data.LIDAR_data = LIDAR_data

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
            logging.info(
                '{} last public validated seq is {}'.format(str(self.data.pulse),
                                                            str(self.data.val_seq)))
        else:
            logging.info(
                '{} last private validated seq is {}'.format(str(self.data.pulse),
                                                             str(self.data.val_seq)))
            logging.info('userid is {}'.format(self.read_uid))


        # logging.info('unval_seq {}, val_seq {}'.format(str(self.data.unval_seq),str(self.data.val_seq)))
        # save data to pickle into saved folder
        self.save_to_pickle('saved')
        # save data to pickle into scratch folder
        self.save_to_pickle('scratch')
        # save KG1 data on different file (needed later when applying corrections)
        self.save_kg1('saved')
        self.data.saved = False
        self.data.data_changed = False
        self.data.statusflag_changed = False
        # dump KG1 data on different file (used to autosave later when applying corrections)
        self.dump_kg1


        if self.data.KG1_data.mode != "Automatic Corrections":
            self.data.KG1_data.correctedby = self.data.KG1_data.mode.split(" ")[2]
            logging.info('{} last validated seq is {} by {}'.format(str(self.data.pulse),
                                                                    str(self.data.val_seq),self.data.KG1_data.correctedby))


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
        # PLOT KG1 data.
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

        ax_all = self.widget_LID_ALL.figure.add_subplot(gs[0])
        ax_14 = self.widget_LID_14.figure.add_subplot(gs[0])
        ax_58 = self.widget_LID_58.figure.add_subplot(gs[0])

        ax_mir = self.widget_MIR.figure.add_subplot(gs[0])

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

            self.widget_LID1.draw()

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
    def update_GUI(self):
        """
        updates GUI after reading data
        :return:
        """
        # now status flag group can be enabled
        self.groupBox_statusflag.setEnabled(True)

        # self.button_plot.setEnabled(True)
        # self.button_check_pulse.setEnabled(True)
        self.button_saveppf.setEnabled(True)
        self.button_save.setEnabled(True)
        self.pushButton_apply.setEnabled(True)
        self.pushButton_makeperm.setEnabled(True)
        self.pushButton_undo.setEnabled(True)
        self.checkSFbutton.setEnabled(True)
        self.comboBox_markers.setEnabled(True)
        self.comboBox_2ndtrace.setEnabled(True)

        self.tabWidget.setCurrentIndex(0)
        self.tabSelected(arg=0)
        self.tabWidget.connect(self.tabWidget,
                               QtCore.SIGNAL("currentChanged(int)"),
                               self.tabSelected)
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

    # ------------------------
    def plot_2nd_trace(self):
        """
        function that plots a second trace in the tabs(each canvas)
        at the moment clears the canvas and re-plot everything
        so probably a little slow.

        :return:
        """
        # self.data.s2ndtrace = self.comboBox_2ndtrace.itemText(i)

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

        # ax_mir = self.widget_MIR.figure.add_subplot(gs[0])

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

            # if chan > 4:
            #     # channels 5-8 have mirror movement
            #     name1 = 'MIR' + str(chan)
            #     ax_name1 = 'ax' + str(chan) + str(1)
            #     widget_name1 = 'widget_LID' + str(chan) + str(1)
            #     vars()[ax_name1].plot(self.data.KG1_data.vibration[chan].time,
            #                           self.data.KG1_data.vibration[chan].data*1e6,
            #                           marker='x', label=name1, color='b',linestyle= 'None')
            #     vars()[ax_name1].legend()
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

                # ax_mir.plot(self.data.KG1_data.vibration[chan].time,
                #             self.data.KG1_data.vibration[chan].data * 1e6,
                #             marker='x', label=name1, linestyle='None')
                # ax_mir.legend()
                # draw_widget(chan)

        logging.info('plotting second trace {}'.format(self.data.s2ndtrace))
        if self.data.s2ndtrace == 'None':
            logging.info('no second trace selected')
        if self.data.s2ndtrace == 'HRTS':
            # check HRTS data exist
            if self.data.HRTS_data is not None:
                # if len(self.data.HRTS_data.density[chan].time) == 0:
                #     logging.info('NO HRTS data')
                # else:
                for chan in self.data.HRTS_data.density.keys():
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
                        self.data.HRTS_data.density[chan], self.data.dis_time)

                    vars()[ax_name].plot(self.data.HRTS_data.density[chan].time,
                                         self.data.HRTS_data.density[chan].data,
                                         label=name, marker='o',
                                         color='orange')
                    vars()[ax_name].legend()

                    # if chan > 4:
                    #     ax_name1 = 'ax' + str(chan) + str(1)
                    #     widget_name1 = 'widget_LID' + str(chan) + str(1)
                    #     vars()[ax_name].plot(
                    #         self.data.HRTS_data.density[chan].time,
                    #         self.data.HRTS_data.density[chan].data, label=name,
                    #         marker='o', color='orange')
            else:
                logging.warning('no {} data'.format(self.data.s2ndtrace))


        if self.data.s2ndtrace == 'Lidar':
            #if len(self.data.LIDAR_data.density[chan].time) == 0:
            if self.data.KG4_data.density is not None:

                for chan in self.data.KG1_data.constants.kg1v.keys():
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
                        self.data.HRTS_data.density[chan], self.data.dis_time)

                    vars()[ax_name].plot(self.data.LIDAR_data.density[chan].time,
                                         self.data.LIDAR_data.density[chan].data,
                                         label=name, marker='o',
                                         color='green')
                    vars()[ax_name].legend()

                    # if chan > 4:
                    #     ax_name1 = 'ax' + str(chan) + str(1)
                    #     widget_name1 = 'widget_LID' + str(chan) + str(1)
                    #     vars()[ax_name].plot(
                    #         self.data.LIDAR_data.density[chan].time,
                    #         self.data.LIDAR_data.density[chan].data, label=name,
                    #         marker='o', color='green')
            else:
                logging.warning('no {} data'.format(self.data.s2ndtrace))

        if self.data.s2ndtrace == 'Far':
            if self.data.KG4_data.faraday is not None:
                # if len(self.data.KG4_data.faraday[chan].time) == 0:
                #     logging.info('NO Far data')
                # else:

                for chan in self.data.KG4_data.faraday.keys():
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
                        self.data.HRTS_data.density[chan],
                        self.data.dis_time)

                    vars()[ax_name].plot(self.data.KG4_data.faraday[chan].time,
                                         self.data.KG4_data.faraday[chan].data,
                                         label=name, marker='o', color='red')
                    vars()[ax_name].legend()

                    # if chan > 4:
                    #     ax_name1 = 'ax' + str(chan) + str(1)
                    #     widget_name1 = 'widget_LID' + str(chan) + str(1)
                    #     vars()[ax_name].plot(self.data.KG4_data.faraday[chan].time,
                    #                          self.data.KG4_data.faraday[chan].data,
                    #                          label=name, marker='o',
                    #                          color='red')
            else:
                logging.warning('no {} data'.format(self.data.s2ndtrace))


        if self.data.s2ndtrace == 'CM':
            if self.data.KG4_data.xg_ell_signal is not None:

                # if len(self.data.KG4_data.xg_ell_signal[chan].time) == 0:
                #     logging.info('NO CM data')
                # else:

                for chan in self.data.KG4_data.xg_ell_signal.keys():
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
                        self.data.HRTS_data.density[chan],
                        self.data.dis_time)

                    vars()[ax_name].plot(self.data.KG4_data.xg_ell_signal[chan].time,
                                         self.data.KG4_data.xg_ell_signal[chan].data,
                                         label=name, marker='o', color='purple')
                    vars()[ax_name].legend()

                    # if chan > 4:
                    #     ax_name1 = 'ax' + str(chan) + str(1)
                    #     widget_name1 = 'widget_LID' + str(chan) + str(1)
                    #     vars()[ax_name].plot(
                    #         self.data.KG4_data.xg_ell_signal[chan].time,
                    #         self.data.KG4_data.xg_ell_signal[chan].data, label=name,
                    #         marker='o', color='purple')
            else:
                logging.warning('no {} data'.format(self.data.s2ndtrace))

        if self.data.s2ndtrace == 'KG1_RT':
            if self.data.KG4_data.density is not None:
                # if len(self.data.KG4_data.density[chan].time) == 0:
                #     logging.info('NO KG1_RT data')
                # else:

                for chan in self.data.KG4_data.density.keys():
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
                        self.data.KG1_data.kg1rt[chan], self.data.HRTS_data.density[chan],
                        self.data.dis_time)

                    vars()[ax_name].plot(self.data.KG1_data.kg1rt[chan].time,
                                         self.data.KG1_data.kg1rt[chan].data,
                                         label=name, marker='o', color='brown')
                    vars()[ax_name].legend()

                    # if chan > 4:
                    #     ax_name1 = 'ax' + str(chan) + str(1)
                    #     widget_name1 = 'widget_LID' + str(chan) + str(1)
                    #     vars()[ax_name].plot(self.data.KG1_data.kg1rt[chan].time,
                    #                          self.data.KG1_data.kg1rt[chan].data,
                    #                          label=name, marker='o',
                    #                          color='brown')

        if self.data.s2ndtrace == 'BremS':
            logging.error('not implemented yet')

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

    # ------------------------
    # noinspection PyUnusedLocal,PyUnusedLocal
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

        self.widget_MIR.figure.clear()
        self.widget_MIR.draw()

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

        ax1 = self.widget_LID1.figure.add_subplot(gs[0])
        ax1_marker = self.widget_LID1.figure.add_subplot(gs[1], sharex=ax1)

        ax2 = self.widget_LID2.figure.add_subplot(gs[0])
        ax2_marker = self.widget_LID2.figure.add_subplot(gs[1], sharex=ax2)

        ax3 = self.widget_LID3.figure.add_subplot(gs[0])
        ax3_marker = self.widget_LID3.figure.add_subplot(gs[1], sharex=ax3)

        ax4 = self.widget_LID4.figure.add_subplot(gs[0])
        ax4_marker = self.widget_LID4.figure.add_subplot(gs[1], sharex=ax4)

        ax5 = self.widget_LID5.figure.add_subplot(gs1[0])
        ax51 = self.widget_LID5.figure.add_subplot(gs1[1], sharex=ax5)
        ax5_marker = self.widget_LID5.figure.add_subplot(gs1[2], sharex=ax5)

        ax6 = self.widget_LID6.figure.add_subplot(gs1[0])
        ax61 = self.widget_LID6.figure.add_subplot(gs1[1], sharex=ax6)
        ax6_marker = self.widget_LID6.figure.add_subplot(gs1[2], sharex=ax6)

        ax7 = self.widget_LID7.figure.add_subplot(gs1[0])
        ax71 = self.widget_LID7.figure.add_subplot(gs1[1], sharex=ax7)
        ax7_marker = self.widget_LID7.figure.add_subplot(gs1[2], sharex=ax7)

        ax8 = self.widget_LID8.figure.add_subplot(gs1[0])
        ax81 = self.widget_LID8.figure.add_subplot(gs1[1], sharex=ax8)
        ax8_marker = self.widget_LID8.figure.add_subplot(gs1[2], sharex=ax8)

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

        if self.data.marker is not None:
            logging.info('plotting marker {}'.format(self.data.marker))
        if self.data.marker == 'None':
            logging.info('no marker selected')

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

        if self.data.marker == 'ELMs':
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
                logging.info('No ELMs marker')

                # if chan > 4:
                #     ax_name1 = 'ax' + str(chan) + str(1)
                #     widget_name1 = 'widget_LID' + str(chan) + str(1)
                #     vars()[ax_name].plot(
                #         self.data.HRTS_data.density[chan].time,
                #         self.data.HRTS_data.density[chan].data, label=name,
                #         marker='o', color='orange')

        if self.data.marker == 'MAGNETICs':
            if (self.data.MAG_data.start_ip) > 0:
                for chan in self.data.KG1_data.density.keys():
                    ax_name = 'ax' + str(chan) + '_marker'
                    # name = 'HRTS ch.' + str(chan)

                    for vert in [self.data.MAG_data.start_ip, self.data.MAG_data.end_ip]:
                        vars()[ax_name].axvline(x=vert, ymin=0, ymax=1,
                                                linewidth=2, color="red")
                    for vert in [self.data.MAG_data.start_flattop,
                                 self.data.MAG_data.end_flattop]:
                        vars()[ax_name].axvline(x=vert, ymin=0, ymax=1,
                                                linewidth=2, color="green")
            else:
                logging.info('No MAGNETICs marker')

        if self.data.marker == 'NBI':
            if (self.data.NBI_data.start_nbi) > 0.0:
                for chan in self.data.KG1_data.density.keys():
                    ax_name = 'ax' + str(chan) + '_marker'
                    # name = 'HRTS ch.' + str(chan)

                    for vert in [self.data.NBI_data.start_nbi,
                                 self.data.NBI_data.end_nbi]:
                        vars()[ax_name].axvline(x=vert, ymin=0, ymax=1,
                                                linewidth=2, color="red")
            else:
                logging.info('No NBI marker')

        if self.data.marker == 'PELLETs':
            if self.data.PELLETS_data.time_pellets is not None:
                for chan in self.data.KG1_data.density.keys():
                    ax_name = 'ax' + str(chan) + '_marker'
                    # name = 'HRTS ch.' + str(chan)

                    for vert in [self.data.PELLETS_data.time_pellets]:
                        vars()[ax_name].axvline(x=vert, ymin=0, ymax=1,
                                                linewidth=2, color="red")
            else:
                logging.info('No PELLET marker')

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



    # ------------------------
    def handle_saveppfbutton(self):

        """
        save data


        user will save either Status Flags or ppf (and SF)

        if user selects in GUI to save ppf a new PPF sequence will be written for dda='KG1V'
        if user selects in GUI to save SF only the SF will be written in the last sequence (no new sequence)

        """

        self.write_uid = self.comboBox_writeuid.currentText()

        # -------------------------------
        # 13. Write data to PPF
        # -------------------------------
        if self.radioButton_storeData.isChecked():
            logging.info(
                '\n Requesting to change ppf data')
            self.areyousure_window = QtGui.QMainWindow()
            self.ui_areyousure = Ui_areyousure_window()
            self.ui_areyousure.setupUi(self.areyousure_window)
            self.areyousure_window.show()

            self.ui_areyousure.pushButton_YES.clicked.connect(
                self.handle_save_data_statusflag)
            self.ui_areyousure.pushButton_NO.clicked.connect(self.handle_no)

        if self.radioButton_storeSF.isChecked():
            logging.info(
                '\n Requesting to change ppf data')
            self.areyousure_window = QtGui.QMainWindow()
            self.ui_areyousure = Ui_areyousure_window()
            self.ui_areyousure.setupUi(self.areyousure_window)
            self.areyousure_window.show()

            self.ui_areyousure.pushButton_YES.clicked.connect(
                self.handle_save_statusflag)
            self.ui_areyousure.pushButton_NO.clicked.connect(self.handle_no)
        else:
            logging.error('\n please select action!')

    # ------------------------
    def handle_save_data_statusflag(self):
        """
        function data handles the writing of a new PPF

        :return: 67 if there has been an error in writing status flag
                0 otherwise (success)
        """

        logger.info("\n\n             Saving KG1 workspace to pickle")



        err = open_ppf(self.data.pulse, self.write_uid)

        if err != 0:
            return 67

        itref_kg1v = -1
        dda = "KG1V"
        return_code = 0

        for chan in self.data.KG1_data.density.keys():
            status = np.empty(
                len(self.data.KG1_data.density[chan].time))
            status.fill(self.data.SF_list[
                            chan - 1])
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
                                                             chan])
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
                                                             chan])

                    if write_err != 0:
                        logger.error(
                            "Failed to write {}/{}. Errorcode {}".format(dda,
                                                                         dtype_jxb,
                                                                         write_err))
                        return write_err
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

        if write_err != 0:
            return 67
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
            return 67
        logger.info("Close PPF.")
        err = close_ppf(self.data.pulse, self.write_uid, self.data.constants.code_version)

        if err != 0:
            return 67

        self.data.saved = True
        self.data.data_changed = True
        self.data.statusflag_changed = True

        self.save_kg1('saved')
        logger.log(5, ' deleting scratch folder')
        delete_files_in_folder('./scratch')
        delete_files_in_folder('./saved')
        logger.log(5, "\n {} - saved is {} - data changed is {} - status flags changed is {}".format(myself(),self.data.saved,self.data.data_changed, self.data.statusflag_changed))
        self.ui_areyousure.pushButton_YES.setChecked(False)

        self.areyousure_window.hide()
        #
        return return_code

    # ------------------------
    def handle_save_statusflag(self):
        """
        function that uses ppfssf inside ppf library (ATTENTION this function is not listed yet in the ppf library python documentation (only C++ version)
        :return: 0 if success
                 68 if fails to write status flags
        """

        return_code = 0


        # Initialise PPF system
        ier = ppfgo(pulse=self.data.pulse)

        if ier != 0:
            return 68

        # Set UID
        ppfuid(self.write_uid, 'w')

        for chan in self.data.KG1_data.density.keys():
            dtype_lid = "LID{}".format(chan)
            (write_err,) = ppfssf(self.data.pulse, self.data.val_seq, 'KG1V', dtype_lid,
                                  self.data.SF_list[chan - 1])
            if write_err != 0:
                logger.error(
                    "Failed to write {}/{} status flag. Errorcode {}".format(
                        'KG1V', dtype_lid,
                        write_err))
            break
        self.ui_areyousure.pushButton_YES.setChecked(False)

        self.areyousure_window.hide()
        logger.info("\n\n     Status flags written to ppf.")
        self.data.saved = True
        self.data_change = True
        self.data.statusflag_changed = True


        self.save_kg1('saved')
        logger.log(5, ' deleting scratch folder')
        delete_files_in_folder('./scratch')

        logger.log(5, "\n {} - saved is {} - data changed is {} - status flags changed is {}".format(myself(),self.data.saved,self.data.data_changed, self.data.statusflag_changed))
        delete_files_in_folder('./saved')

        return return_code

    # ------------------------

    def handle_normalizebutton(self):
        """
        function thtat normalises the second trace to KG1 for comparing purposes during validation and fringe correction
        :return:
        """

        if self.data.s2ndtrace == 'None':
            pass
        else:
            logging.info('\n Normalizing')
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

                name = self.data.s2ndtrace + ' ch.' + str(chan)
                vars()[ax_name].plot(self.data.secondtrace_original[chan].time,
                                     self.data.secondtrace_norm[chan].data,
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
            logging.info('\n signals have been normalized')

    # ------------------------
    def handle_button_restore(self):
        """
        function that restores signals to original amplitude
        :return:
        """

        if self.data.s2ndtrace == 'None':
            pass
        else:
            logging.info('restoring signals to original amplitude')
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
            logging.info('signals have been restored')

    # ------------------------
    def handle_applybutton(self):
        """
        function that applies correction

        :return:
        """
        pass

    # ------------------------
    def handle_makepermbutton(self):
        """
        function that makes permanenet last correction
        :return:
        """
        pass

    # ------------------------
    def handle_undobutton(self):
        """
        function to undo last correction
        :return:
        """
        pass

    def check_current_tab(self):
        """
        return current tab
        :return: current tab
        """
        return self.QTabWidget.currentWidget()

    # ----------------------------
    @staticmethod
    def handle_help_menu():
        """
        opens Chrome browser to read HTML documentation
        :return:
        """
        import webbrowser
        url = 'file://' + os.path.realpath('../docs/_build/html/index.html')
        webbrowser.get(using='google-chrome').open(url, new=2)

        # ----------------------------

    @staticmethod
    def handle_pdf_open():
        """

        :return: opens pdf file of the guide
        """
        file = os.path.realpath('../docs/CORMATpy_GUI_Documentation.pdf')
        import subprocess

        subprocess.Popen(['okular', file])

    # ----------------------------

    # ----------------------------
    def handle_exit_button(self):
        """
        Exit the application
        """
        if self.data.pulse is None:
            logger.log(5,'no data has been loaded, it is save to exit')

            self.areyousure_window = QtGui.QMainWindow()
            self.ui_areyousure = Ui_areyousure_window()
            self.ui_areyousure.setupUi(self.areyousure_window)
            self.areyousure_window.show()

            self.ui_areyousure.pushButton_YES.clicked.connect(
                self.handle_yes_exit)
            self.ui_areyousure.pushButton_NO.clicked.connect(
                self.handle_no)

            #logging.info('\n Exit now')
            #sys.exit()
        elif hasattr(self, 'KG1_data') is False:
            logger.log(5,'no data has been loaded, it is save to exit')

            self.areyousure_window = QtGui.QMainWindow()
            self.ui_areyousure = Ui_areyousure_window()
            self.ui_areyousure.setupUi(self.areyousure_window)
            self.areyousure_window.show()

            self.ui_areyousure.pushButton_YES.clicked.connect(
                self.handle_yes_exit)
            self.ui_areyousure.pushButton_NO.clicked.connect(
                self.handle_no)

            #logging.info('\n Exit now')
            #sys.exit()

#        try:
            # if data have been modified
            #data_changed = equalsFile('./saved/' + str(self.data.pulse) + '_kg1.pkl',
                                      #'./scratch/' + str(
                                          #self.data.pulse) + '_kg1.pkl')
        elif (self.data.data_changed | self.data.statusflag_changed) is True:
            logger.log(5, "data changed? {} status flags changed? {}".format(self.data.data_changed, self.data.statusflag_changed))
            if self.data.saved:
                logger.log(5,"data has been saved")
                self.handle_yes_exit()
            else:
                logger.info('\n data has not been saved do you want to exit? \n')

                self.areyousure_window = QtGui.QMainWindow()
                self.ui_areyousure = Ui_areyousure_window()
                self.ui_areyousure.setupUi(self.areyousure_window)
                self.areyousure_window.show()

                self.ui_areyousure.pushButton_YES.clicked.connect(
                    self.handle_yes_exit)
                self.ui_areyousure.pushButton_NO.clicked.connect(
                    self.handle_no)
        else:
            logging.info('data and status flags have not changed, it is save to exit')
            #self.handle_yes_exit()

            self.areyousure_window = QtGui.QMainWindow()
            self.ui_areyousure = Ui_areyousure_window()
            self.ui_areyousure.setupUi(self.areyousure_window)
            self.areyousure_window.show()

            self.ui_areyousure.pushButton_YES.clicked.connect(
                self.handle_yes_exit)
            self.ui_areyousure.pushButton_NO.clicked.connect(
                self.handle_no)
    #except AttributeError:
        #logging.info('\n')
        #logging.info('Exit now')
        #sys.exit()

    @staticmethod
    def handle_yes_exit():
        """
        close application
        :return:
        """

        #logging.info('\n')
        logging.info('\n Exit now')
        QtCore.QCoreApplication.instance().quit()
        sys.exit()







def main():
    """
    Main function

    the only input to the GUI is the debug

    by default is set to INFO
    """

    app = QtGui.QApplication(sys.argv)
    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()
    width, height = [800,600]
    MainWindow = CORMAT_GUI()
    screenShape = QtGui.QDesktopWidget().screenGeometry()
    logger.log(5, 'screen resolution is {} x {}'.format(width, height))
    # 1366x768 vnc viewer size

    
    time.sleep(3.0)
    MainWindow.show()
    # MainWindow.resize(screenShape.width(), screenShape.height())
    # MainWindow.showMaximized()
    app.exec_()
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

    logging.addLevelName(5, "DEBUG_PLUS")

    logger.setLevel(level=debug_map[args.debug])

    logger = logging.getLogger(__name__)





    fmt = MyFormatter()
    hdlr = logging.StreamHandler(sys.stdout)

    hdlr.setFormatter(fmt)
    logging.root.addHandler(hdlr)
    fh = handlers.RotatingFileHandler('./LOGFILE.DAT', mode = 'w',maxBytes=(1048576*5), backupCount=7)
    fh.setFormatter(fmt)
    logging.root.addHandler(fh)


    main()


    

    