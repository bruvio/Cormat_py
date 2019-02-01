#!/usr/bin/env python


# ----------------------------
__author__ = "Bruno Viola"
__Name__ = "KG1 data validation tool" 
__version__ = "0.1"
__release__ = "0"
__maintainer__ = "Bruno Viola"
__email__ = "bruno.viola@ukaea.uk"
__status__ = "Testing"
#__status__ = "Production"
__credits__ = ["aboboc"]


from shutil import copyfile
import sys
import logging
import platform
import argparse
import pdb
from ppf_write import *
#from pickle import dump,load
import pickle
from os import listdir
#  pdb.set_trace()
from consts import Consts
# from kg1_consts import Kg1Consts
from mag_data import MagData
from areyousure_gui import Ui_areyousure_window
# from kg1_data import Kg1Data
from kg1_ppf_data import Kg1PPFData
from kg4_data import Kg4Data
from elms_data import ElmsData
from pellet_data import PelletData
from nbi_data import NBIData
from hrts_data import HRTSData
from signal_base import SignalBase
from lidar_data import LIDARData
from find_disruption import find_disruption
import woop
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar



import argparse
from pathlib import Path
import logging
import pathlib
import numpy as np
from ppf import *
from PyQt4 import Qt, QtCore,QtGui
from matplotlib import cm
from plotdata import Ui_plotdata_window
from matplotlib import gridspec
from scipy import interpolate
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import subprocess
import os

#import library containing useful function
from library import *


import matplotlib.pyplot as plt
plt.rcParams["savefig.directory"] = os.chdir(os.getcwd())

logger = logging.getLogger(__name__)



class QPlainTextEditLogger(logging.Handler):
    """
    class that defines a handler to write logging message inside the GUI
    the geometry and position of the TextEdit is defined here, not by QT designer
    """



    def __init__(self, parent):
        super().__init__()
        self.widget = QtGui.QPlainTextEdit(parent)
        self.widget.setGeometry(1070,610,381,191)

        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class woop(QtGui.QMainWindow, woop.Ui_CORMAT_py,QPlainTextEditLogger):
    """

    Main control function for Woop GUI.



    """
    def _initialize_widget(self,widget):
        """
        function that:
         - initialises every tab (widget)
         - add layout
         - add navigation toolbar and position it at the bottom of the tab
        :param widget:
        :return:
        """
        widget.figure.clear()
        widget.draw()

        widget.setLayout(QtGui.QVBoxLayout())
        widget.layout().setContentsMargins(0, 710, 50, -0)#(left, top, right, bottom)
        widget.layout().setSpacing(0)
        toolbar = NavigationToolbar(widget, self)
        widget.layout().addWidget(toolbar)
        widget.figure.clear()
        widget.draw()

    # ----------------------------
    def __init__(self, parent=None):
        """
        Setup the GUI, and connect the buttons to functions.

        Initialise widgets and canvas.
        Define defaults


        """


        import os
        super(woop, self).__init__(parent)
        self.setupUi(self)
        ###setting up the logger to write inside a Text box

        logTextBox = QPlainTextEditLogger(self)
        # You can format what is printed to text box
        # logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.DEBUG)

        #initialising new pulse checkbox to false
        self.checkBox_newpulse.setChecked(False)


        # initialising tabs
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

        #set tabwidget index to 0 - lid1 is the tab shown at startup
        # self.tabWidget.setCurrentWidget(self.tabWidget.findChild(tabWidget, 'tab_LID1'))
        self.tabWidget.setCurrentIndex(0)


        # initialising folders


        logging.debug('start')
        cwd = os.getcwd()
        self.workfold = cwd
        self.home = cwd
        parent= Path(self.home)

        self.edge2dfold = str(parent.parent) + '/EDGE2D'
        if "USR" in os.environ:
            logging.debug('USR in env')
            # self.owner = os.getenv('USR')
            self.owner = os.getlogin()
        else:
            logging.debug('using getuser to authenticate')
            import getpass
            self.owner = getpass.getuser()

        logging.debug('this is your username {}'.format(self.owner))


        self.homefold = os.path.join(os.sep, 'u', self.owner)
        logging.debug('this is your homefold {}'.format(self.homefold))

        home = str(Path.home())

        self.chain1 = '/common/chain1/kg1/'
        extract_history(
            self.workfold +'/run_out.txt',
            self.chain1 + 'cormat_out.txt')
        logging.info('copying to local user profile')


        logging.debug('we are in %s', cwd)
        # psrint(homefold + os.sep+ folder)

        logger.info("\n Reading in constants.")
        try:
            self.constants = Consts("consts.ini", __version__)
            # constants = Kg1Consts("kg1_consts.ini", __version__)
        except KeyError:
            logger.error("\n Could not read in configuration file consts.ini")
            sys.exit(65)
        
        # list of authorized user to write KG1 ppfs
        read_uis = []
        for user in self.constants.readusers.keys():
            user_name = self.constants.readusers[user]
            read_uis.append(user_name)
        

        





        self.exit_button.clicked.connect(self.handle_exit_button)
        self.PathTranfile = None

        self.PathCatalog = '/home'

        write_uis = []

        #check if owner is in list of authorised users
        if self.owner in read_uis:
            logging.info('user {} authorised to write public PPF'.format(self.owner))
            write_uis.insert(0,'JETPPF') # jetppf first in the combobox list
            write_uis.append(self.owner)
            # users.append('chain1')
        else:
            logging.info('user {} NOT authorised to write public PPF'.format(self.owner))
            write_uis.append(self.owner)


        #initialise combobox
        self.comboBox_readuid.addItems(read_uis)
        self.comboBox_writeuid.addItems(write_uis)

        #set combobox index to 1 so that the default write_uid is owner
        if len(write_uis) ==2:
            self.comboBox_writeuid.setCurrentIndex(1)
        else:
            self.comboBox_writeuid.setCurrentIndex(0)


        #set default pulse
        # initpulse = pdmsht()
        initpulse = 92121
        self.lineEdit_jpn.setText(str(initpulse))



        othersignallist=['None','HRTS','Lidar','BremS','Far','CM','KG1_RT']
        self.comboBox_2ndtrace.addItems(othersignallist)
        self.comboBox_2ndtrace.activated[str].connect(self.plot_2nd_trace)

        markers=['None','ELMs','NBI','PELLETs','MAGNETICs']
        self.comboBox_markers.addItems(markers)
        self.comboBox_markers.activated[str].connect(self.plot_markers)

        self.comboBox_markers.setEnabled(False)
        self.comboBox_2ndtrace.setEnabled(False)




        # self.pushButton_plot.clicked.connect(self.handle_plotbutton)
        # self.pushButton_zoom.clicked.connect(self.handle_zoombutton)
        # self.pushButton_reset.clicked.connect(self.handle_resetbutton)
        self.button_read_pulse.clicked.connect(self.handle_readbutton)
        # self.button_check_pulse.clicked.connect(self.handle_checkbutton)
        self.button_save.clicked.connect(self.handle_savebutton)

        self.button_normalize.clicked.connect(self.handle_normalizebutton)
        self.button_restore.clicked.connect(self.handle_button_restore)

        self.pushButton_apply.clicked.connect(self.handle_applybutton)
        self.pushButton_makeperm.clicked.connect(self.handle_makepermbutton)
        self.pushButton_undo.clicked.connect(self.handle_undobutton)

        self.checkSFbutton.clicked.connect(self.checkStatuFlags)


        #setting code folders
        try:
            #figure folder
            pathlib.Path(cwd + os.sep + 'figures').mkdir(parents=True,exist_ok=True)
            # scratch folder - where you keep unsaved unfinished data
            pathlib.Path(cwd + os.sep + 'scratch').mkdir(parents=True,exist_ok=True)
            # save foldere - where you keep saved pulse data
            pathlib.Path(cwd + os.sep + 'saved').mkdir(parents=True,exist_ok=True)
            # standard set - where you keep signal list to be used in the code
            pathlib.Path(cwd + os.sep + 'standard_set').mkdir(parents=True,exist_ok=True)
        except:
            raise SystemExit('failed to initialise folders')



        #disable many button to avoid conflicts
        self.button_save.setEnabled(False)
        self.checkSFbutton.setEnabled(False)
        self.button_normalize.setEnabled(False)
        self.pushButton_apply.setEnabled(False)
        self.pushButton_makeperm.setEnabled(False)
        self.pushButton_undo.setEnabled(False)
        self.button_restore.setEnabled(False)

        #run code by default
        # self.button_read_pulse.click()

        #initialize to zero status flag radio buttons
        self.radioButton_statusflag_0.setChecked(False)
        self.radioButton_statusflag_1.setChecked(False)
        self.radioButton_statusflag_2.setChecked(False)
        self.radioButton_statusflag_3.setChecked(False)
        self.radioButton_statusflag_4.setChecked(False)

        #set




        # self.pushButton_reset.setEnabled(False)
        # self.pushButton_plot.setEnabled(False)
        # self.pushButton_zoom.setEnabled(False)

        #set status flag radio buttons to false
        self.groupBox_statusflag.setEnabled(False)
        #set read uid combo box to disabled
        self.comboBox_readuid.setEnabled(False)


        #check selected tab
        # self.tabSelected(arg=0)
        # self.tabWidget.connect(self.tabWidget,
        #                        QtCore.SIGNAL("currentChanged(int)"),
        #                        self.tabSelected)
        # self.tabWidget.(
        #     lambda: self.tabWidget.currentIndex())

        #to disable a tab use
        # self.tabWidget.setTabEnabled(3, False)

        self.checkBox_newpulse.toggled.connect(
            lambda: self.check_status(self.checkBox_newpulse))



    def check_status(self,button_newpulse):
        """
        check if button "newpulse" is clicked


        :param button:
        :return: disable/enable combobox
        """
        if button_newpulse.isChecked() == True:
            logging.debug('{} is checked'.format(button_newpulse.objectName()))
            self.comboBox_readuid.setEnabled(True)
        elif button_newpulse.isChecked() == False:
            logging.debug('{} is NOT checked'.format(button_newpulse.objectName()))
            self.comboBox_readuid.setEnabled(False)



    # ------------------------
    def checkStatuFlags(self):
        """
        reads the list containing pulse status flag
        :return:
        """

        self.SF_list = [int(self.SF_ch1),
                        int(self.SF_ch2),
                        int(self.SF_ch3),
                        int(self.SF_ch4),
                        int(self.SF_ch5),
                        int(self.SF_ch6),
                        int(self.SF_ch7),
                        int(self.SF_ch8)]

        logging.info('%s has the following SF %s', str(self.pulse), self.SF_list)
    # ------------------------
    # ------------------------
    # def radiobutton_status(self):
        # self.radioButton_statusflag_0.toggled.connect

    # ------------------------

    # ------------------------
    def tabSelected(self, arg=None):
        """
        function that convert arg number into tab name
        :param arg:
        :return:
        """
        if arg == 0:
            self.current_tab = 'LID_1'
            self.set_status_flag_radio(self.SF_ch1)
        if arg == 1:
            self.current_tab = 'LID_2'
            self.set_status_flag_radio(self.SF_ch2)
        if arg == 2:
            self.current_tab = 'LID_3'
            self.set_status_flag_radio(self.SF_ch3)
        if arg == 3:
            self.current_tab = 'LID_4'
            self.set_status_flag_radio(self.SF_ch4)
        if arg == 4:
            self.current_tab = 'LID_5'
            self.set_status_flag_radio(self.SF_ch5)
        if arg == 5:
            self.current_tab = 'LID_6'
            self.set_status_flag_radio(self.SF_ch6)
        if arg == 6:
            self.current_tab = 'LID_7'
            self.set_status_flag_radio(self.SF_ch7)
        if arg == 7:
            self.current_tab = 'LID_8'
            self.set_status_flag_radio(self.SF_ch8)
        if arg == 8:
            self.current_tab = 'LID_1-4'
        if arg == 9:
            self.current_tab = 'LID_5-8'
        if arg == 10:
            self.current_tab = 'LID_ALL'
        if arg == 11:
            self.current_tab = 'MIR'

        logging.debug('\n\t: current Tab is {}'.format(self.current_tab))



    def checkstate(self, button):
        """
        connect tab number to LID channel and sets status flag
        :param button:
        :return:
        """
        snd = self.sender()
        #old status flag
        if self.current_tab == 'LID_1':
            SF_old = self.SF_ch1
        if self.current_tab == 'LID_2':
            SF_old = self.SF_ch2
        if self.current_tab == 'LID_3':
            SF_old = self.SF_ch3
        if self.current_tab == 'LID_4':
            SF_old = self.SF_ch4
        if self.current_tab == 'LID_5':
            SF_old = self.SF_ch5
        if self.current_tab == 'LID_6':
            SF_old = self.SF_ch6
        if self.current_tab == 'LID_7':
            SF_old = self.SF_ch7
        if self.current_tab == 'LID_8':
            SF_old = self.SF_ch8

        SF = snd.objectName().split('_')[2]  # statusflag value selected

        # logging.debug('{} has status flag {}'.format(self.current_tab,str(SF_old)))

        if self.current_tab == 'LID_1':
            self.SF_ch1 = SF
        if self.current_tab == 'LID_2':
            self.SF_ch2 = SF
        if self.current_tab == 'LID_3':
            self.SF_ch3 = SF
        if self.current_tab == 'LID_4':
            self.SF_ch4 = SF
        if self.current_tab == 'LID_5':
            self.SF_ch5 = SF
        if self.current_tab == 'LID_6':
            self.SF_ch6 = SF
        if self.current_tab == 'LID_7':
            self.SF_ch7 = SF
        if self.current_tab == 'LID_8':
            self.SF_ch8 = SF

        # logging.debug(
        #     '{} new status flag is {}'.format(self.current_tab, str(SF)))

        # print(snd.objectName(),SF)
            # if SF == 0:

            # self.set_status_flag_radio(SF)
            #
            # self.current_tab
            # self.ui_plotdata.checkBox.setChecked(False)
    # ------------------------
    # def whatTab(self):
    #     currentIndex=self.tabWidget.currentIndex()
    #     currentWidget=self.tabWidget.currentWidget()

    def set_status_flag_radio(self,value):
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

    # ------------------------
    def load_pickle(self):
        logging.info('\n loading pulse data')
        # Python 3: open(..., 'rb')
        with open('./saved/' + str(self.pulse) + '.pkl',
                  'rb') as f:

            [self.pulse, self.KG1_data,
             self.KG4_data, self.MAG_data, self.PELLETS_data,
             self.ELM_data, self.HRTS_data,
             self.NBI_data, self.is_dis, self.dis_time,
             self.LIDAR_data] = pickle.load(f)
        f.close()
        with open('./saved/' + str(self.pulse) + '_kg1.pkl',
                  'rb') as f:  # Python 3: open(..., 'rb')
            [self.KG1_data,self.SF_list,self.unval_seq, self.val_seq,self.read_uid] = pickle.load(f)
        f.close()
        logging.info('\n workspace loaded')
        logging.info('\n workspace data comes from userid {}'.format(self.read_uid))
        logging.info('{} has the following SF {}'.format(str(self.pulse), self.SF_list))
        logging.info('{} last validated seq is {}'.format(str(self.pulse),str(self.val_seq)))

        [self.SF_ch1,
         self.SF_ch2,
         self.SF_ch3,
         self.SF_ch4,
         self.SF_ch5,
         self.SF_ch6,
         self.SF_ch7,
         self.SF_ch8] = self.SF_list




    # ------------------------
    def save_to_pickle(self):
        logging.info('\n saving pulse data')
        with open('./saved/' + str(self.pulse) + '.pkl', 'wb') as f:
            pickle.dump(
                [self.pulse, self.KG1_data,
                 self.KG4_data, self.MAG_data, self.PELLETS_data,
                 self.ELM_data, self.HRTS_data,
                 self.NBI_data, self.is_dis, self.dis_time,
                 self.LIDAR_data], f)
        f.close()
        logging.info('\n data saved')

    # ------------------------
    def save_kg1(self):
        logging.info('\n saving KG1 data')
        with open('./saved/' + str(self.pulse) + '_kg1.pkl', 'wb') as f:
            pickle.dump([self.KG1_data,self.SF_list,self.unval_seq, self.val_seq,self.read_uid],f)
        f.close()
        logging.info('\n kg1 data saved')



# ------------------------
    def handle_readbutton(self):

        #status flag groupbox is disabled
        self.groupBox_statusflag.setEnabled(False)
        self.tabWidget.setCurrentIndex(0)


        #disable "normalize" and "restore" buttons
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

        self.kg1_original = {}
        self.kg1_norm = {}

        # define now two gridspecs
        # gs is the gridspec per channels 1-4
        # gs1 is the gridspec for channels 5-8
        # when plotting markers they will allocate space to plot markers in a subplot under current plot

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



        # read pulse number
        self.pulse = int(self.lineEdit_jpn.text())
        logging.info('\n')
        logger.info("Reading data for pulse {}".format(str(self.pulse)))



        #check if KG1 data for selected pulse already exists in 'saved' folder
        exists = os.path.isfile('./saved/'+str(self.pulse)+'.pkl')


        if exists:
            logging.debug('file {} found in local workspace'.format('./saved/'+str(self.pulse)+'.pkl'))

            if  (self.checkBox_newpulse.isChecked() == False):
                logging.debug('{} is not checked'.format(self.checkBox_newpulse.objectName()))
                # if exists and new pulse checkbox is not checked then load data
                logging.info('\n')
                logging.info('pulse data already downloaded')
                self.load_pickle()
                # self.tabWidget.setCurrentIndex(0)
                # self.tabSelected(arg=0)

            else:
                logging.debug('{} is  checked'.format(self.checkBox_newpulse.objectName()))
                logging.info('\n')
                # if exists and and new pulse checkbox is checked then ask for confirmation if user wants to carry on
                logging.info('pulse data already downloaded - you are requesting to download again')
                self.areyousure_window = QtGui.QMainWindow()
                self.ui_areyousure = Ui_areyousure_window()
                self.ui_areyousure.setupUi(self.areyousure_window)
                self.areyousure_window.show()

                self.ui_areyousure.pushButton_YES.clicked.connect(self.handle_yes)
                self.ui_areyousure.pushButton_NO.clicked.connect(self.handle_no)

        else:
            logging.debug('no file {} found in local workspace')
            #if data not exists read it and overwrite

            self.readdata()








        # -------------------------------
        # 0. PLOT KG1 data.
        # -------------------------------

        for chan in self.KG1_data.density.keys():
            ax_name=  'ax'+str(chan)
            name='LID'+str(chan)
            widget_name='widget_LID'+str(chan)


            self.kg1_norm[chan] = SignalBase(self.constants)
            self.kg1_norm[chan].data = norm(self.KG1_data.density[chan].data)

            vars()[ax_name].plot(self.KG1_data.density[chan].time, self.KG1_data.density[chan].data,label=name,marker='x', color='b',linestyle= 'None')
            vars()[ax_name].legend()
            ax_all.plot(self.KG1_data.density[chan].time, self.KG1_data.density[chan].data,label=name,marker='x',linestyle= 'None')
            ax_all.legend()
            if chan < 5:
                ax_14.plot(self.KG1_data.density[chan].time,
                                 self.KG1_data.density[chan].data, label=name,
                                 marker='x',linestyle= 'None')
                ax_14.legend()

            if chan > 4:
                ax_58.plot(self.KG1_data.density[chan].time,
                                 self.KG1_data.density[chan].data, label=name,
                                 marker='x',linestyle= 'None')
                ax_58.legend()

            self.widget_LID1.draw()

            if chan >4:
                name1='MIR'+str(chan)
                name2 = 'JxB' + str(chan)
                ax_name1 = 'ax' + str(chan)+str(1)
                widget_name1 = 'widget_LID' + str(chan)+str(1)
                axx = vars()[ax_name1]
                vars()[ax_name1].plot(self.KG1_data.vibration[chan].time,
                                      self.KG1_data.vibration[chan].data*1e6,marker='x',label=name1, color='b',linestyle= 'None')
                vars()[ax_name1].plot(self.KG1_data.jxb[chan].time,
                                      self.KG1_data.jxb[chan].data*1e6,marker='x',label=name2, color='c',linestyle= 'None')
                vars()[ax_name1].legend()


                ax_mir.plot(self.KG1_data.vibration[chan].time,
                                 self.KG1_data.vibration[chan].data*1e6,marker='x',label=name1,linestyle= 'None')
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



        #now status flag group can be enabled
        self.groupBox_statusflag.setEnabled(True)

        # self.button_plot.setEnabled(True)
        # self.button_check_pulse.setEnabled(True)
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
        #set combobox index to 1 so that the default write_uid is owner
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



    # ----------------------------
    def handle_no(self):
        """
        functions that ask to confirm if user wants NOT to proceed

        to set read data for selected pulse
    """

        # button_name = button.objectName()
        # print(button_name)

        logging.info('\n')
        logging.debug('pressed %s button', self.ui_areyousure.pushButton_NO.text())
        logging.debug('go back and perform a different action')


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



        logging.info('\n')
        logging.debug('pressed %s button',
                      self.ui_areyousure.pushButton_YES.text())
        logging.debug('continue')
        self.readdata()




        #status flag groupbox is disabled
        self.groupBox_statusflag.setEnabled(False)
        self.checkSFbutton.setEnabled(False)
        self.comboBox_markers.setEnabled(False)
        #disable "normalize" and "restore" buttons
        self.button_normalize.setEnabled(False)
        self.button_restore.setEnabled(False)
        self.comboBox_2ndtrace.setCurrentIndex(0)
        self.comboBox_markers.setCurrentIndex(0)

        # define now two gridspecs
        # gs is the gridspec per channels 1-4
        # gs1 is the gridspec for channels 5-8
        # when plotting markers they will allocate space to plot markers in a subplot under current plot

        # gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])# working: creates canvas with 2 columns in the ratio 1/3

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





        # -------------------------------
        # 0. PLOT KG1 data.
        # -------------------------------

        for chan in self.KG1_data.density.keys():
            ax_name = 'ax' + str(chan)
            name = 'LID' + str(chan)
            widget_name = 'widget_LID' + str(chan)

            self.kg1_norm[chan] = SignalBase(self.constants)
            self.kg1_norm[chan].data = norm(self.KG1_data.density[chan].data)

            vars()[ax_name].plot(self.KG1_data.density[chan].time,
                                 self.KG1_data.density[chan].data, label=name,
                                 marker='x', color='b',linestyle= 'None')
            vars()[ax_name].legend()
            ax_all.plot(self.KG1_data.density[chan].time,
                             self.KG1_data.density[chan].data, label=name,
                             marker='x',linestyle= 'None')
            ax_all.legend()
            if chan < 5:
                ax_14.plot(self.KG1_data.density[chan].time,
                                self.KG1_data.density[chan].data, label=name,
                                marker='x',linestyle= 'None')
                ax_14.legend()

            if chan > 4:
                ax_58.plot(self.KG1_data.density[chan].time,
                                self.KG1_data.density[chan].data, label=name,
                                marker='x',linestyle= 'None')
                ax_58.legend()

            self.widget_LID1.draw()

            if chan > 4:
                name1 = 'MIR' + str(chan)
                name2 = 'JxB' + str(chan)

                ax_name1 = 'ax' + str(chan) + str(1)

                widget_name1 = 'widget_LID' + str(chan) + str(1)
                vars()[ax_name1].plot(self.KG1_data.vibration[chan].time,
                                      self.KG1_data.vibration[chan].data*1e6,
                                      marker='x', label=name1, color='b',linestyle= 'None')
                vars()[ax_name1].plot(self.KG1_data.jxb[chan].time,
                                      self.KG1_data.jxb[chan].data*1e6,marker='x',label=name2, color='c',linestyle= 'None')
                vars()[ax_name1].legend()
                ax_mir.plot(self.KG1_data.vibration[chan].time,
                                 self.KG1_data.vibration[chan].data*1e6, marker='x',linestyle= 'None',
                                 label=name1)
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


        self.ui_areyousure.pushButton_YES.setChecked(False)

        self.areyousure_window.hide()

        #now status flag groupbox can be enabled
        # self.button_plot.setEnabled(True)
        # self.button_check_pulse.setEnabled(True)
        self.button_save.setEnabled(True)
        self.comboBox_markers.setEnabled(True)
        self.comboBox_2ndtrace.setEnabled(True)
        # self.button_normalize.setEnabled(True)
        # self.button_restore.setEnabled(True)
        self.pushButton_apply.setEnabled(True)
        self.pushButton_makeperm.setEnabled(True)
        self.pushButton_undo.setEnabled(True)
        self.groupBox_statusflag.setEnabled(True)
        self.comboBox_markers.setEnabled(True)
        self.comboBox_2ndtrace.setEnabled(True)
        self.checkSFbutton.setEnabled(True)
        self.tabWidget.setCurrentIndex(0)
        self.tabSelected(arg=0)






        self.tabWidget.connect(self.tabWidget,
                               QtCore.SIGNAL("currentChanged(int)"),
                               self.tabSelected)
        #set combobox index to 1 so that the default write_uid is owner
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


# -----------------------
    def readdata(self):
        """
        function that reads data as described in const.ini

        reads:
        - mag data
        - pellet data
        - elm data
        - kg1 data
        - kg4 data
        - nbi data
        - hrts data
        - lidar data



        :return: save data to pickle files: one just for KG1 (pulsename_kg1) and one for everything else (pulsename.pkl)
        """




        # -------------------------------
        # 1. Read in Magnetics data
        # -------------------------------
        logger.info("\n             Reading in magnetics data.")
        MAG_data = MagData(self.constants)
        success = MAG_data.read_data(self.pulse)
        self.MAG_data = MAG_data

        # -------------------------------
        # 2. Read in KG1 data
        # -------------------------------
        logger.info("\n             Reading in KG1 data.")
        KG1_data = Kg1PPFData(self.constants, self.pulse)
        self.KG1_data = KG1_data

        self.read_uid = self.comboBox_readuid.currentText()

        success = KG1_data.read_data(self.pulse, read_uid=self.read_uid)

        # Exit if there were no good signals
        # If success == 1 it means that at least one channel was not available. But this shouldn't stop the rest of the code
        # from running.
        if success != 0 and success != 1:
            # success = 11: Validated PPF data is already available for all channels
            # success = 8: No good JPF data was found
            # success = 9: JPF data was bad
            sys.exit(success)

            # -------------------------------
        # -------------------------------
        # 4. Read in KG4 data
        # -------------------------------
        logger.info("\n             Reading in KG4 data.")
        KG4_data = Kg4Data(self.constants)
        KG4_data.read_data(self.MAG_data, self.pulse)
        self.KG4_data = KG4_data
        # pdb.set_trace()

        # -------------------------------
        # 5. Read in pellet signals
        # -------------------------------
        logger.info("\n             Reading in pellet data.")
        PELLETS_data = PelletData(self.constants)
        PELLETS_data.read_data(self.pulse)
        self.PELLETS_data = PELLETS_data
        # -------------------------------
        # 6. Read in NBI data.
        # -------------------------------
        logger.info("\n             Reading in NBI data.")
        NBI_data = NBIData(self.constants)
        NBI_data.read_data(self.pulse)
        self.NBI_data = NBI_data
        # -------------------------------
        # 7. Check for a disruption, and set status flag near the disruption to 4
        #    If there was no disruption then dis_time elements are set to -1.
        #    dis_time is a 2 element list, being the window around the disruption.
        #    Within this time window the code will not make corrections.
        # -------------------------------
        logger.info("\n             Find disruption.")
        is_dis, dis_time = find_disruption(self.pulse, self.constants,
                                           self.KG1_data)
        self.is_dis = is_dis
        self.dis_time = dis_time[0]
        logger.info("Time of disruption {}".format(dis_time[0]))

        # -------------------------------
        # 8. Read in Be-II signals, and find ELMs
        # -------------------------------
        logger.info("\n             Reading in ELMs data.")
        ELM_data = ElmsData(self.constants, self.pulse, dis_time=dis_time[0])
        self.ELM_data = ELM_data
        # -------------------------------
        # 9. Read HRTS data
        # # -------------------------------
        logger.info("\n             Reading in HRTS data.")
        HRTS_data = HRTSData(self.constants)
        HRTS_data.read_data(self.pulse)
        self.HRTS_data = HRTS_data
        # # # # -------------------------------
        # # # 10. Read LIDAR data
        # # # -------------------------------
        logger.info("\n             Reading in LIDAR data.")
        LIDAR_data = LIDARData(self.constants)
        LIDAR_data.read_data(self.pulse)
        self.LIDAR_data = LIDAR_data

        #read status flag

        self.SF_list = check_SF(self.read_uid,self.pulse)

        [self.SF_ch1,
         self.SF_ch2,
         self.SF_ch3,
         self.SF_ch4,
         self.SF_ch5,
         self.SF_ch6,
         self.SF_ch7,
         self.SF_ch8 ] = self.SF_list

        self.unval_seq, self.val_seq = get_min_max_seq(self.pulse, dda="KG1V", read_uid=self.read_uid)
        if self.read_uid.lower() == 'jetppf':
            logging.info('{} last public validated seq is {}'.format(str(self.pulse),str(self.val_seq)))
        else:
            logging.info('{} last private validated seq is {}'.format(str(self.pulse),str(self.val_seq)))
            logging.info('userid is {}'.format(self.read_uid))
        # logging.info('unval_seq {}, val_seq {}'.format(str(self.unval_seq),str(self.val_seq)))
        # save data to pickle
        self.save_to_pickle()
        # save KG1 data on different file (needed later when applying corrections)
        self.save_kg1()




    # ------------------------
    def plot_2nd_trace(self):
        """
        function that plots a second trace in the tabs(each canvas)
        at the moment clears the canvas and re-plot everything
        so probably a little slow.

        :return:
        """
        # self.s2ndtrace = self.comboBox_2ndtrace.itemText(i)


        self.comboBox_markers.setCurrentIndex(0)
        self.secondtrace_original = {}
        self.secondtrace_norm = {}


        self.s2ndtrace = self.comboBox_2ndtrace.currentText()


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

        # for every channel in KG1 (8 channels)
        for chan in self.KG1_data.density.keys():
            ax_name = 'ax' + str(chan)
            name = 'LID' + str(chan)
            widget_name = 'widget_LID' + str(chan)

            vars()[ax_name].plot(self.KG1_data.density[chan].time,
                                 self.KG1_data.density[chan].data,
                                 label=name, marker='x', color='b',linestyle= 'None')
            vars()[ax_name].legend()
            # self.widget_LID1.draw()

            if chan > 4:
                # channels 5-8 have mirror movement
                name1 = 'MIR' + str(chan)
                ax_name1 = 'ax' + str(chan) + str(1)
                widget_name1 = 'widget_LID' + str(chan) + str(1)
                vars()[ax_name1].plot(self.KG1_data.vibration[chan].time,
                                      self.KG1_data.vibration[chan].data*1e6,
                                      marker='x', label=name1, color='b',linestyle= 'None')
                vars()[ax_name1].legend()


        logging.info('plotting second trace {}'.format(self.s2ndtrace))
        if self.s2ndtrace == 'None':
            logging.info('no second trace selected')
        if self.s2ndtrace == 'HRTS':
            #check HRTS data exist
            if self.HRTS_data is not None:
            # if len(self.HRTS_data.density[chan].time) == 0:
            #     logging.info('NO HRTS data')
            # else:
                for chan in self.HRTS_data.density.keys():
                    ax_name = 'ax' + str(chan)
                    name = 'HRTS ch.' + str(chan)
                    widget_name = 'widget_LID' + str(chan)

                    self.secondtrace_original[chan] = SignalBase(self.constants)
                    self.secondtrace_norm[chan] = SignalBase(self.constants)

                    self.secondtrace_original[chan].time = self.HRTS_data.density[chan].time
                    self.secondtrace_original[chan].data = self.HRTS_data.density[chan].data
                    # self.secondtrace_norm[chan].data = norm(self.HRTS_data.density[chan].data)
                    self.secondtrace_norm[chan].data = normalise(self.HRTS_data.density[chan],self.HRTS_data.density[chan],self.dis_time)

                    vars()[ax_name].plot(self.HRTS_data.density[chan].time,
                                         self.HRTS_data.density[chan].data,
                                         label=name, marker='o',
                                         color='orange')
                    vars()[ax_name].legend()

                    # if chan > 4:
                    #     ax_name1 = 'ax' + str(chan) + str(1)
                    #     widget_name1 = 'widget_LID' + str(chan) + str(1)
                    #     vars()[ax_name].plot(
                    #         self.HRTS_data.density[chan].time,
                    #         self.HRTS_data.density[chan].data, label=name,
                    #         marker='o', color='orange')

        if self.s2ndtrace == 'Lidar':
            if len(self.LIDAR_data.density[chan].time) == 0:
                logging.info('NO LIDAR data')
            else:

                for chan in self.KG1_data.constants.kg1v.keys():
                    ax_name = 'ax' + str(chan)
                    name = 'Lidar ch.' + str(chan)
                    widget_name = 'widget_LID' + str(chan)

                    self.secondtrace_original[chan] = SignalBase(self.constants)
                    self.secondtrace_norm[chan] = SignalBase(self.constants)

                    self.secondtrace_original[chan].time = self.LIDAR_data.density[chan].time
                    self.secondtrace_original[chan].data = self.LIDAR_data.density[chan].data
                    # self.secondtrace_norm[chan].data = norm(self.LIDAR_data.density[chan].data)
                    self.secondtrace_norm[chan].data = normalise(self.LIDAR_data.density[chan],self.HRTS_data.density[chan],self.dis_time)



                    vars()[ax_name].plot(self.LIDAR_data.density[chan].time,
                                         self.LIDAR_data.density[chan].data,
                                         label=name, marker='o',
                                         color='green')
                    vars()[ax_name].legend()

                    # if chan > 4:
                    #     ax_name1 = 'ax' + str(chan) + str(1)
                    #     widget_name1 = 'widget_LID' + str(chan) + str(1)
                    #     vars()[ax_name].plot(
                    #         self.LIDAR_data.density[chan].time,
                    #         self.LIDAR_data.density[chan].data, label=name,
                    #         marker='o', color='green')

        if self.s2ndtrace == 'Far':
         if self.KG4_data.faraday is not None:
            # if len(self.KG4_data.faraday[chan].time) == 0:
            #     logging.info('NO Far data')
            # else:

            for chan in self.KG4_data.faraday.keys():
                ax_name = 'ax' + str(chan)
                name = 'Far ch.' + str(chan)
                widget_name = 'widget_LID' + str(chan)

                self.secondtrace_original[chan] = SignalBase(self.constants)
                self.secondtrace_norm[chan] = SignalBase(self.constants)

                self.secondtrace_original[chan].time = self.KG4_data.faraday[
                    chan].time
                self.secondtrace_original[chan].data = self.KG4_data.faraday[
                    chan].data
                # self.secondtrace_norm[chan].data = norm(self.KG4_data.faraday[chan].data)
                self.secondtrace_norm[chan].data = normalise(
                    self.KG4_data.faraday[chan], self.HRTS_data.density[chan],
                    self.dis_time)

                vars()[ax_name].plot(self.KG4_data.faraday[chan].time,
                                     self.KG4_data.faraday[chan].data,
                                     label=name, marker='o', color='red')
                vars()[ax_name].legend()

                # if chan > 4:
                #     ax_name1 = 'ax' + str(chan) + str(1)
                #     widget_name1 = 'widget_LID' + str(chan) + str(1)
                #     vars()[ax_name].plot(self.KG4_data.faraday[chan].time,
                #                          self.KG4_data.faraday[chan].data,
                #                          label=name, marker='o',
                #                          color='red')

        if self.s2ndtrace == 'CM':
         if self.KG4_data.xg_ell_signal is not None:

            # if len(self.KG4_data.xg_ell_signal[chan].time) == 0:
            #     logging.info('NO CM data')
            # else:

            for chan in self.KG4_data.xg_ell_signal.keys():
                ax_name = 'ax' + str(chan)
                name = 'CM ch.' + str(chan)
                widget_name = 'widget_LID' + str(chan)

                self.secondtrace_original[chan] = SignalBase(self.constants)
                self.secondtrace_norm[chan] = SignalBase(self.constants)

                self.secondtrace_original[chan].time = self.KG4_data.xg_ell_signal[
                    chan].time
                self.secondtrace_original[chan].data = self.KG4_data.xg_ell_signal[
                    chan].data
                # self.secondtrace_norm[chan].data = norm(
                #     self.KG4_data.xg_ell_signal[chan].data)
                self.secondtrace_norm[chan].data = normalise(
                    self.KG4_data.xg_ell_signal[chan], self.HRTS_data.density[chan],
                    self.dis_time)

                vars()[ax_name].plot(self.KG4_data.xg_ell_signal[chan].time,
                                     self.KG4_data.xg_ell_signal[chan].data,
                                     label=name, marker='o', color='purple')
                vars()[ax_name].legend()

                # if chan > 4:
                #     ax_name1 = 'ax' + str(chan) + str(1)
                #     widget_name1 = 'widget_LID' + str(chan) + str(1)
                #     vars()[ax_name].plot(
                #         self.KG4_data.xg_ell_signal[chan].time,
                #         self.KG4_data.xg_ell_signal[chan].data, label=name,
                #         marker='o', color='purple')

        if self.s2ndtrace == 'KG1_RT':
         if self.KG4_data.density is not None:
            # if len(self.KG4_data.density[chan].time) == 0:
            #     logging.info('NO KG1_RT data')
            # else:

            for chan in self.KG4_data.density.keys():
                ax_name = 'ax' + str(chan)
                name = 'KG1 RT ch.' + str(chan)
                widget_name = 'widget_LID' + str(chan)

                self.secondtrace_original[chan] = SignalBase(self.constants)
                self.secondtrace_norm[chan] = SignalBase(self.constants)

                self.secondtrace_original[chan].time = self.KG1_data.kg1rt[
                    chan].time
                self.secondtrace_original[chan].data = self.KG1_data.kg1rt[
                    chan].data
                # self.secondtrace_norm[chan].data = norm(
                #     self.KG1_data.kg1rt[chan].data)
                self.secondtrace_norm[chan].data = normalise(
                    self.KG1_data.kg1rt[chan], self.HRTS_data.density[chan],
                    self.dis_time)

                vars()[ax_name].plot(self.KG1_data.kg1rt[chan].time,
                                     self.KG1_data.kg1rt[chan].data,
                                     label=name, marker='o', color='brown')
                vars()[ax_name].legend()

                # if chan > 4:
                #     ax_name1 = 'ax' + str(chan) + str(1)
                #     widget_name1 = 'widget_LID' + str(chan) + str(1)
                #     vars()[ax_name].plot(self.KG1_data.kg1rt[chan].time,
                #                          self.KG1_data.kg1rt[chan].data,
                #                          label=name, marker='o',
                #                          color='brown')

        if self.s2ndtrace == 'BremS':
            logging.debug('not implemented yet')

        # update canvas
        self.widget_LID1.draw()
        self.widget_LID2.draw()
        self.widget_LID3.draw()
        self.widget_LID4.draw()
        self.widget_LID5.draw()
        self.widget_LID6.draw()
        self.widget_LID7.draw()
        self.widget_LID8.draw()

        #only now activate button "normalize" and "restore"
        self.button_normalize.setEnabled(True)
        self.button_restore.setEnabled(True)


# ------------------------
    def plot_markers(self):
        """
        function that plots a marker traces in the tabs(each canvas)
        This version creates sub plot inside the canvas
        :return:
        """
        # self.s2ndtrace = self.comboBox_2ndtrace.itemText(i)
        self.comboBox_2ndtrace.setCurrentIndex(0)
        self.marker = self.comboBox_markers.currentText()

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

        # define now other gridspecs
        # gs2 is the gridspec per channels 1-4
        # gs21 is the gridspec for channels 5-8
        # when plotting NO markers they will reset to standard plots

        heights2 = [4]
        gs2 = gridspec.GridSpec(ncols=1, nrows=1, height_ratios=heights2)
        heights21 = [3, 3]
        gs21 = gridspec.GridSpec(ncols=1, nrows=2, height_ratios=heights21)



        for chan in self.KG1_data.density.keys():
            ax_name = 'ax' + str(chan)
            name = 'LID' + str(chan)
            widget_name = 'widget_LID' + str(chan)
            vars()[ax_name].plot(self.KG1_data.density[chan].time,
                                 self.KG1_data.density[chan].data,
                                 label=name, marker='x', color='b',linestyle= 'None')
            vars()[ax_name].legend()
            self.widget_LID1.draw()

            if chan > 4:
                name1 = 'MIR' + str(chan)
                ax_name1 = 'ax' + str(chan) + str(1)
                widget_name1 = 'widget_LID' + str(chan) + str(1)
                vars()[ax_name1].plot(self.KG1_data.vibration[chan].time,
                                      self.KG1_data.vibration[chan].data*1e6,
                                      marker='x', label=name1, color='b',linestyle= 'None')
                vars()[ax_name1].legend()


        if self.marker is not None:
            logging.info('plotting marker {}'.format(self.marker))
        if self.marker == 'None':
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








        if self.marker == 'ELMs':
            if self.ELM_data.elm_times is not None:
                for chan in self.KG1_data.density.keys():
                        ax_name = 'ax' + str(chan)+'_marker'
                        # name = 'HRTS ch.' + str(chan)
                        widget_name = 'widget_LID' + str(chan)

                        vars()[ax_name].plot(self.ELM_data.elms_signal.time, self.ELM_data.elms_signal.data,
                                             color='black')

                        for vert in self.ELM_data.elm_times:
                            vars()[ax_name].axvline(x=vert, ymin=0, ymax=1,
                                                 linewidth=2, color="red")
                    # if len(self.ELM_data.elm_times) > 0:
                        for horz in [self.ELM_data.UP_THRESH, self.ELM_data.DOWN_THRESH]:
                            vars()[ax_name].axhline(y=horz, xmin=0, xmax=1,
                                            linewidth=2, color="cyan")
            else:
                logging.info('No ELMs marker')

                        # if chan > 4:
                        #     ax_name1 = 'ax' + str(chan) + str(1)
                        #     widget_name1 = 'widget_LID' + str(chan) + str(1)
                        #     vars()[ax_name].plot(
                        #         self.HRTS_data.density[chan].time,
                        #         self.HRTS_data.density[chan].data, label=name,
                        #         marker='o', color='orange')

        if self.marker == 'MAGNETICs':
            if (self.MAG_data.start_ip) > 0:
                for chan in self.KG1_data.density.keys():
                    ax_name = 'ax' + str(chan)+'_marker'
                    # name = 'HRTS ch.' + str(chan)
                    widget_name = 'widget_LID' + str(chan)


                    for vert in [self.MAG_data.start_ip, self.MAG_data.end_ip]:
                        vars()[ax_name].axvline(x=vert, ymin=0, ymax=1,
                                            linewidth=2, color="red")
                    for vert in [self.MAG_data.start_flattop, self.MAG_data.end_flattop]:
                        vars()[ax_name].axvline(x=vert, ymin=0, ymax=1,
                                            linewidth=2, color="green")
            else:
                logging.info('No MAGNETICs marker')


        if self.marker == 'NBI':
            if (self.NBI_data.start_nbi) > 0.0:
                for chan in self.KG1_data.density.keys():
                        ax_name = 'ax' + str(chan)+'_marker'
                        # name = 'HRTS ch.' + str(chan)
                        widget_name = 'widget_LID' + str(chan)


                        for vert in [self.NBI_data.start_nbi, self.NBI_data.end_nbi]:
                            vars()[ax_name].axvline(x=vert, ymin=0, ymax=1,
                                                    linewidth=2, color="red")
            else:
                logging.info('No NBI marker')




        if self.marker == 'PELLETs':
            if self.PELLETS_data.time_pellets is not None:
                for chan in self.KG1_data.density.keys():
                    ax_name = 'ax' + str(chan)+'_marker'
                    # name = 'HRTS ch.' + str(chan)
                    widget_name = 'widget_LID' + str(chan)


                    for vert in [self.PELLETS_data.time_pellets]:
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

    # ------------------------

    def handle_checkbutton(self):
        pass

#------------------------
    def handle_savebutton(self):


        """
        save data
        user can save either Status Flags or ppf (and SF)
        :return:
        """

        logging.info('\n')
        # if exists and and new pulse checkbox is checked then ask for confirmation if user wants to carry on
        logging.info(
            'Requesting to change ppf data')

        self.write_uid = self.comboBox_writeuid.currentText()

        # -------------------------------
        # 13. Write data to PPF
        #     Don't allow for writing of new PPF if write UID is JETPPF and test is true.
        #     This is since with test set we can over-write manually corrected data.
        # -------------------------------
        if self.radioButton_storeData.isChecked() == True:
            self.areyousure_window = QtGui.QMainWindow()
            self.ui_areyousure = Ui_areyousure_window()
            self.ui_areyousure.setupUi(self.areyousure_window)
            self.areyousure_window.show()

            self.ui_areyousure.pushButton_YES.clicked.connect(self.handle_save_data_statusflag)
            self.ui_areyousure.pushButton_NO.clicked.connect(self.handle_no)


        if self.radioButton_storeSF.isChecked() == True:
            self.areyousure_window = QtGui.QMainWindow()
            self.ui_areyousure = Ui_areyousure_window()
            self.ui_areyousure.setupUi(self.areyousure_window)
            self.areyousure_window.show()

            self.ui_areyousure.pushButton_YES.clicked.connect(self.handle_save_statusflag)
            self.ui_areyousure.pushButton_NO.clicked.connect(self.handle_no)



#------------------------
    def handle_save_data_statusflag(self):
        logger.info("\n             Saving KG1 workspace to pickle")
        self.save_kg1()

        err = open_ppf(self.pulse, self.write_uid)

        if err != 0:
            return 67

        itref_kg1v = -1
        dda = "KG1V"
        return_code = 0

        for chan in self.KG1_data.density.keys():
            status = np.empty(
                len(self.KG1_data.density[chan].time));
            status.fill(self.SF_list[
                            chan - 1])
            dtype_lid = "LID{}".format(chan)
            comment = "DATA FROM KG1 CHANNEL {}".format(chan)
            write_err, itref_written = write_ppf(self.pulse, dda, dtype_lid,
                                                 self.KG1_data.density[
                                                     chan].data,
                                                 time=self.KG1_data.density[
                                                     chan].time,
                                                 comment=comment,
                                                 unitd='M-2', unitt='SEC',
                                                 itref=itref_kg1v,
                                                 nt=len(self.KG1_data.density[
                                                     chan].time),
                                                 status=self.KG1_data.status[
                                                     chan],
                                                 global_status=self.SF_list[
                                                     chan - 1])

            if write_err != 0:
                logger.error(
                    "Failed to write {}/{}. Errorcode {}".format(dda, dtype_lid,
                                                                 write_err))
                break
            # Corrected FJs for vertical channels
            if chan <= 4 and chan in self.KG1_data.fj_dcn.keys():

            # DCN fringes
                if self.KG1_data.fj_dcn is not None:
                    dtype_fc = "FC{}".format(chan)
                    comment = "DCN FRINGE CORRECTIONS CH.{}".format(chan)
                    write_err, itref_written = write_ppf(self.pulse, dda,
                                                         dtype_fc, self.KG1_data.fj_dcn[chan].data,
                                                         time=self.KG1_data.fj_dcn[chan].time,
                                                         comment=comment,
                                                         unitd=" ", unitt="SEC",
                                                         itref=itref_kg1v,
                                                         nt=len(self.KG1_data.fj_dcn[chan].time),
                                                         status=None)

                    if write_err != 0:
                        logger.error(
                            "Failed to write {}/{}. Errorcode {}".format(dda,
                                                                         dtype_fc,
                                                                         write_err))
                        break
                    # if write_err != 0:
                    #     return write_err, itref
            # Vibration data and JXB for lateral channels, and corrected FJ
            elif chan > 4 and chan in self.KG1_data.vibration.keys():
                if self.KG1_data.vibration is not None:
                    # Vibration
                    dtype_vib = "MIR{}".format(chan)
                    comment = "MOVEMENT OF MIRROR {}".format(chan)
                    write_err, itref_written = write_ppf(self.pulse, dda,
                                                         dtype_vib,
                                                         self.KG1_data.vibration[chan].data,
                                                         time=self.KG1_data.vibration[chan].time,
                                                         comment=comment,
                                                         unitd='M', unitt='SEC',
                                                         itref=itref_kg1v,
                                                         nt=len(self.KG1_data.vibration[chan].time),
                                                         status=self.KG1_data.status[chan])
                    if write_err != 0:
                        logger.error(
                            "Failed to write {}/{}. Errorcode {}".format(dda,
                                                                         dtype_vib,
                                                                         write_err))
                        break

                    # JXB movement
                    dtype_jxb = "JXB{}".format(chan)
                    comment = "JxB CALC. MOVEMENT CH.{}".format(chan)
                    write_err, itref_written = write_ppf(self.pulse, dda,
                                                         dtype_jxb, self.KG1_data.jxb[chan].data,
                                                         time=self.KG1_data.jxb[chan].time,
                                                         comment=comment,
                                                         unitd='M', unitt='SEC',
                                                         itref=itref_kg1v,
                                                         nt=len(self.KG1_data.jxb[chan].time),
                                                         status=self.KG1_data.status[chan])

                    if write_err != 0:
                        logger.error(
                            "Failed to write {}/{}. Errorcode {}".format(dda,
                                                                         dtype_jxb,
                                                                         write_err))
                        break
            elif chan > 4 and chan in self.KG1_data.fj_met.keys():
                    # MET fringes
                    if self.KG1_data.fj_met is not None :
                        dtype_fc = "MC{} ".format(chan)
                        comment = "MET FRINGE CORRECTIONS CH.{}".format(chan)
                        write_err, itref_written = write_ppf(self.pulse, dda,
                                                             dtype_fc,
                                                             self.KG1_data.fj_met[chan].data,
                                                             time=self.fj_met[chan].time,
                                                             comment=comment,
                                                             unitd=" ", unitt="SEC",
                                                             itref=-1,
                                                             nt=len(self.KG1_data.fj_met[chan].time),
                                                             status=None)

                        if write_err != 0:
                            logger.error(
                                "Failed to write {}/{}. Errorcode {}".format(
                                    dda,
                                    dtype_fc,
                                    write_err))
                            break

        if write_err != 0:
            return 67
        # Write mode DDA

        mode = "Correct.done by {}".format(self.owner)
        dtype_mode = "MODE"
        comment = mode
        write_err, itref_written = write_ppf(self.pulse, dda, dtype_mode,
                                             np.array([1]),
                                             time=np.array([0]),
                                             comment=comment, unitd=" ",
                                             unitt=" ", itref=-1, nt=1,
                                             status=None)
        # Retrieve geometry data & write to PPF
        temp, r_ref, z_ref, a_ref, r_coord, z_coord, a_coord, coord_err = self.KG1_data.get_coord(
            self.pulse)

        if coord_err != 0:
            return coord_err

        dtype_temp = "TEMP"
        comment = "Vessel temperature(degC)"
        write_err, itref_written = write_ppf(self.pulse, dda, dtype_temp, np.array([temp]),
                                             time=np.array([0]), comment=comment, unitd="deg", unitt="none",
                                             itref=-1, nt=1, status=None)

        geom_chan = np.arange(len(a_ref)) + 1
        dtype_aref = "AREF"
        comment = "CHORD(20 DEC.C): ANGLE"
        write_err, itref_written = write_ppf(self.pulse, dda, dtype_aref, a_ref,
                                             time=geom_chan, comment=comment, unitd="RADIANS", unitt="CHORD NO",
                                             itref=-1, nt=len(geom_chan), status=None)

        dtype_rref = "RREF"
        comment = "CHORD(20 DEC.C): RADIUS"
        write_err, itref_written = write_ppf(self.pulse, dda, dtype_rref, r_ref,
                                             time=geom_chan, comment=comment, unitd="M", unitt="CHORD NO",
                                             itref=itref_written, nt=len(geom_chan), status=None)

        dtype_zref = "ZREF"
        comment = "CHORD(20 DEC.C): HEIGHT"
        write_err, itref_written = write_ppf(self.pulse, dda, dtype_zref, z_ref,
                                             time=geom_chan, comment=comment, unitd="M", unitt="CHORD NO",
                                             itref=itref_written, nt=len(geom_chan), status=None)

        dtype_a = "A   "
        comment = "CHORD: ANGLE"
        write_err, itref_written = write_ppf(self.pulse, dda, dtype_a, a_coord,
                                             time=geom_chan, comment=comment, unitd="RADIANS", unitt="CHORD NO",
                                             itref=itref_written, nt=len(geom_chan), status=None)

        dtype_r = "R   "
        comment = "CHORD: RADIUS"
        write_err, itref_written = write_ppf(self.pulse, dda, dtype_r, r_coord,
                                             time=geom_chan, comment=comment, unitd="M", unitt="CHORD NO",
                                             itref=itref_written, nt=len(geom_chan), status=None)

        dtype_z = "Z   "
        comment = "CHORD: HEIGHT"
        write_err, itref_written = write_ppf(self.pulse, dda, dtype_z, z_coord,
                                             time=geom_chan, comment=comment, unitd="M", unitt="CHORD NO",
                                             itref=itref_written, nt=len(geom_chan), status=None)


        if write_err != 0:
            return 67
        logger.info("Close PPF.")
        err = close_ppf(self.pulse, self.write_uid, self.constants.code_version)

        if err != 0:
            return 67


        self.ui_areyousure.pushButton_YES.setChecked(False)

        self.areyousure_window.hide()
        #
        return return_code


# ------------------------
    def handle_save_statusflag(self):

        return_code = 0

        # Initialise PPF system
        ier = ppfgo(pulse=self.pulse)

        if ier != 0:
            return 68

        # Set UID
        ppfuid(self.write_uid, 'w')

        for chan in self.KG1_data.density.keys():
            dtype_lid = "LID{}".format(chan)
            (write_err,) = ppfssf(self.pulse, self.val_seq, 'KG1V', dtype_lid, self.SF_list[chan - 1])
            if write_err != 0:
                logger.error(
                "Failed to write {}/{} status flag. Errorcode {}".format('KG1V', dtype_lid,
                                                             write_err))
            break
        self.ui_areyousure.pushButton_YES.setChecked(False)

        self.areyousure_window.hide()
        logger.info("\n     Status flags written to ppf.")

        return return_code
# ------------------------



    def handle_normalizebutton(self):

        if self.s2ndtrace == 'None':
            pass
        else:
            logging.info('normalizing')
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
            if self.s2ndtrace == 'HRTS':
                color = 'orange'
            if self.s2ndtrace == 'Lidar':
                color = 'green'
            if self.s2ndtrace == 'Far':
                color = 'red'
            if self.s2ndtrace == 'CM':
                color = 'purple'
            if self.s2ndtrace == 'KG1_RT':
                color = 'brown'
            if self.s2ndtrace == 'BremS':
                color = 'grey'

            # for every channel in KG1 (8 channels)



            for chan in self.KG1_data.density.keys():
                ax_name = 'ax' + str(chan)
                name = 'LID' + str(chan)
                widget_name = 'widget_LID' + str(chan)
                vars()[ax_name].plot(self.KG1_data.density[chan].time,
                                     self.KG1_data.density[chan].data, # kg1_norm
                                     label=name, marker='x', color='b',
                                     linestyle='None')
                vars()[ax_name].legend()

                name = self.s2ndtrace + ' ch.' + str(chan)
                vars()[ax_name].plot(self.secondtrace_original[chan].time,
                                     self.secondtrace_norm[chan].data,
                                     label=name, marker='o',
                                     color=color)
                vars()[ax_name].legend()
                # self.widget_LID1.draw()

                if chan > 4:
                    # channels 5-8 have mirror movement
                    name1 = 'MIR' + str(chan)
                    ax_name1 = 'ax' + str(chan) + str(1)
                    widget_name1 = 'widget_LID' + str(chan) + str(1)
                    vars()[ax_name1].plot(self.KG1_data.vibration[chan].time,
                                          self.KG1_data.vibration[chan].data*1e6,
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
            logging.info('signals have been normalized')

    #------------------------
    def handle_button_restore(self):

        if self.s2ndtrace == 'None':
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
            if self.s2ndtrace == 'HRTS':
                color = 'orange'
            if self.s2ndtrace == 'Lidar':
                color = 'green'
            if self.s2ndtrace == 'Far':
                color = 'red'
            if self.s2ndtrace == 'CM':
                color = 'purple'
            if self.s2ndtrace == 'KG1_RT':
                color = 'brown'
            if self.s2ndtrace == 'BremS':
                color = 'grey'
            # for every channel in KG1 (8 channels)


            for chan in self.KG1_data.density.keys():
                ax_name = 'ax' + str(chan)
                name = 'LID' + str(chan)
                widget_name = 'widget_LID' + str(chan)
                vars()[ax_name].plot(self.KG1_data.density[chan].time,
                                     self.KG1_data.density[chan].data,
                                     label=name, marker='x', color='b',
                                     linestyle='None')
                vars()[ax_name].legend()

                name = self.s2ndtrace + ' ch.' + str(chan)
                vars()[ax_name].plot(self.secondtrace_original[chan].time,
                                     self.secondtrace_original[chan].data,
                                     label=name, marker='o',
                                     color=color)
                vars()[ax_name].legend()
                # self.widget_LID1.draw()

                if chan > 4:
                    # channels 5-8 have mirror movement
                    name1 = 'MIR' + str(chan)
                    ax_name1 = 'ax' + str(chan) + str(1)
                    widget_name1 = 'widget_LID' + str(chan) + str(1)
                    vars()[ax_name1].plot(self.KG1_data.vibration[chan].time,
                                          self.KG1_data.vibration[chan].data*1e6,
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

#------------------------
    def handle_applybutton(self):
        pass

#------------------------
    def handle_makepermbutton(self):
        pass

#------------------------
    def handle_undobutton(self):
        pass



    def check_current_tab(self):
        return self.QTabWidget.currentWidget()

# ----------------------------
    def handle_exit_button(self):
        """
        Exit the application
        """
        self.areyousure_window = QtGui.QMainWindow()
        self.ui_areyousure = Ui_areyousure_window()
        self.ui_areyousure.setupUi(self.areyousure_window)
        self.areyousure_window.show()

        self.ui_areyousure.pushButton_YES.clicked.connect(
            self.handle_yes_exit)
        self.ui_areyousure.pushButton_NO.clicked.connect(self.handle_no)




    def handle_yes_exit(self):

        logging.info('\n')
        logging.info('Exit now')
        sys.exit()



# ----------------------------
# Custom formatter
class MyFormatter(logging.Formatter):
    """
    class to handle the logging formatting
    """
    err_fmt = "%(levelname)-8s %(message)s"
    dbg_fmt = "%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"
    info_fmt = "%(levelname)-8s %(message)s"

    # def __init__(self):
    #     super().__init__(fmt="%(levelno)d: %(msg)s", datefmt=None, style='%')

    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._style._fmt = MyFormatter.dbg_fmt

        elif record.levelno == logging.INFO:
            self._style._fmt = MyFormatter.info_fmt

        elif record.levelno == logging.ERROR:
            self._style._fmt = MyFormatter.err_fmt

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result
#
# def is_python_64bit():
#     return (struct.calcsize("P") == 8)

def main():
    """
    Main function

    the only input to the GUI is the debug

    by default is set to INFO
    """
    logger.info("Running WOOP.")
    import sys
    app = QtGui.QApplication(sys.argv)
    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()
    print(width,height)


    # frm = QtGui.QFrame()
    # frm.sizeHint = lambda: QtCore.QSize(width, height)



    MainWindow = woop()
    # MainWindow.width=200
    # MainWindow.height = 200
    screenShape = QtGui.QDesktopWidget().screenGeometry()
    MainWindow.resize(screenShape.width(), screenShape.height())
    # MainWindow.resize(200,200)
    MainWindow.show()
    #MainWindow.showMaximized()
    app.exec_()


if __name__ == '__main__':
    # Ensure we are running on 64bit
    assert (platform.architecture()[0] == '64bit'), "Please log on Freja"

    # Ensure we are running python 3
    assert sys.version_info >= (3, 5), "Python version too old. Please use >= 3.5.X."

    parser = argparse.ArgumentParser(description='Run GO_woop')
    parser.add_argument("-d", "--debug", type=int,
                        help="Debug level. 0: Info, 1: Warning, 2: Debug,"
                            " 3: Error; \n default level is INFO", default=2)
    parser.add_argument("-doc", "--documentation", type=str,
                        help="Make documentation. yes/no", default='no')



    args = parser.parse_args(sys.argv[1:])
    debug_map = {0: logging.INFO,
                1: logging.WARNING,
                2: logging.DEBUG,
                3: logging.ERROR}

    logger = logging.getLogger(__name__)
    fmt = MyFormatter()
    hdlr = logging.StreamHandler(sys.stdout)

    hdlr.setFormatter(fmt)
    logging.root.addHandler(hdlr)

    logging.root.setLevel(level=debug_map[args.debug])
    main()

