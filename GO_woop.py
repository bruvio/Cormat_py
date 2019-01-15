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



import sys
import logging
import argparse
import pdb

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

from scipy import interpolate
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import subprocess
import os


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


class woop(QtGui.QMainWindow, woop.Ui_MainWindow,QPlainTextEditLogger):
    """

    Main control function for Woop GUI.



    """


    # ----------------------------
    def __init__(self, parent=None):
        """
        Setup the GUI, and connect the buttons to functions.
        """


        import os
        super(woop, self).__init__(parent)
        self.setupUi(self)
        logTextBox = QPlainTextEditLogger(self)
        # You can format what is printed to text box
        # logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.DEBUG)

        self.checkBox_newpulse.setChecked(False)

        # toolBar1 = NavigationToolbar(self.widget_LID1, self)
        # toolBar2 = NavigationToolbar(self.widget_LID2, self)
        # toolBar3 = NavigationToolbar(self.widget_LID3, self)
        # toolBar4 = NavigationToolbar(self.widget_LID4, self)
        # toolBar5 = NavigationToolbar(self.widget_LID5, self)
        # toolBar6 = NavigationToolbar(self.widget_LID6, self)
        # toolBar7 = NavigationToolbar(self.widget_LID7, self)
        # toolBar8 = NavigationToolbar(self.widget_LID8, self)
        # toolBarALL = NavigationToolbar(self.widget_LID_ALL, self)
        # toolBarMIR = NavigationToolbar(self.widget_MIR, self)
        # self.addToolBar(toolBar1)
        # self.addToolBar(toolBar2)
        # self.addToolBar(toolBar3)
        # self.addToolBar(toolBar4)
        # self.addToolBar(toolBar5)
        # self.addToolBar(toolBar6)
        # self.addToolBar(toolBar7)
        # self.addToolBar(toolBar8)
        # self.addToolBar(toolBarALL)
        # self.addToolBar(toolBarMIR)


        self.widget_LID1.figure.clear()
        self.widget_LID1.draw()

        # self.navi_toolbar = NavigationToolbar( self.widget_LID1, self) #createa navigation toolbar for our plot canvas

        # self.vbl = QtGui.QVBoxLayout()
        # self.vbl.addWidget( self.widget_LID1 )
        # self.vbl.addWidget(self.navi_toolbar)
        # self.setLayout( self.vbl )
        # self.navigation_toolbar = NavigationToolbar(self.widget_LID1, self)
        # self.navigation_toolbar.update()

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

        self.widget_LID_ALL.figure.clear()
        self.widget_LID_ALL.draw()

        self.widget_MIR.figure.clear()
        self.widget_MIR.draw()


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
        # :TODO
        #     if self.owner not in read_uis list then disable write ppf and hide write_uid combobox

        self.homefold = os.path.join(os.sep, 'u', self.owner)
        logging.debug('this is your homefold {}'.format(self.homefold))

        home = str(Path.home())

        # cwd = os.getcwd()
        # self.home = cwd
        # print(self.home)
        # print(owner)
        logging.debug('we are in %s', cwd)
        # psrint(homefold + os.sep+ folder)

        logger.info("Reading in constants.")
        try:
            self.constants = Consts("consts.ini", __version__)
            # constants = Kg1Consts("kg1_consts.ini", __version__)
        except KeyError:
            logger.error("Could not read in configuration file consts.ini")
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


        # for user in self.constants.writeusers.keys():
        #     user_name = self.constants.writeusers[user]
        #     write_uis.append(user_name)

        # users = [u for u in listdir(self.PathCatalog)]
        write_uis = []
        # users=sorted(users)
        write_uis.insert(0,'JETPPF')
        # users.append('JETPPF')
        # users.append('chain1')
        write_uis.append(self.owner)


        # fsm = Qt.QFileSystemModel()
        # index = fsm.setRootPath(self.PathCatalog)
        # self.comboBox = Qt.QComboBox()

        # self.comboBox_readuid.setModel(fsm)
        # self.comboBox_readuid.setRootModelIndex(index)
        self.comboBox_readuid.addItems(read_uis)
        self.comboBox_writeuid.addItems(write_uis)
        # initpulse = pdmsht()
        initpulse = 92121
        self.lineEdit_jpn.setText(str(initpulse))



        othersignallist=['None','HRTS','Lidar','BremS','Far','CM','KG1_RT']
        self.comboBox_2ndtrace.addItems(othersignallist)
        self.comboBox_2ndtrace.activated[str].connect(self.plot_2nd_trace)

        markers=['None','ELMs','NBI','PELLETs','MAGNETICs']
        self.comboBox_markers.addItems(markers)
        self.comboBox_markers.activated[str].connect(self.plot_markers)

        # self.ui_edge2d.comboBox_Name.setModel(fsm)
        # self.ui_edge2d.comboBox_Name.setRootModelIndex(index)
        # self.comboBox_2ndtrace.currentIndexChanged.connect(self.plot_2nd_trace)

        # write_allowedusers = []
        # # write_allowedusers.append(self.owner)
        # # write_allowedusers.append('JETPPF')
        # write_allowedusers.append(users)





        # self.pushButton_plot.clicked.connect(self.handle_plotbutton)
        # self.pushButton_zoom.clicked.connect(self.handle_zoombutton)
        # self.pushButton_reset.clicked.connect(self.handle_resetbutton)
        self.button_read_pulse.clicked.connect(self.handle_readbutton)
        self.button_check_pulse.clicked.connect(self.handle_checkbutton)
        self.button_save.clicked.connect(self.handle_savebutton)
        self.button_normalize.clicked.connect(self.handle_normalizebutton)
        self.pushButton_apply.clicked.connect(self.handle_applybutton)
        self.pushButton_makeperm.clicked.connect(self.handle_makepermbutton)
        self.pushButton_undo.clicked.connect(self.handle_undobutton)


        #setting code folders

        #figure folder
        pathlib.Path(cwd + os.sep + 'figures').mkdir(parents=True,exist_ok=True)
        # scratch folder - where you keep unsaved unfinished data
        pathlib.Path(cwd + os.sep + 'scratch').mkdir(parents=True,exist_ok=True)
        # save foldere - where you keep saved pulse data
        pathlib.Path(cwd + os.sep + 'saved').mkdir(parents=True,exist_ok=True)
        # standard set - where you keep signal list to be used in the code
        pathlib.Path(cwd + os.sep + 'standard_set').mkdir(parents=True,exist_ok=True)

        #disable many button to avoid conflicts
        self.button_save.setEnabled(False)
        self.button_normalize.setEnabled(False)
        self.pushButton_apply.setEnabled(False)
        self.pushButton_makeperm.setEnabled(False)
        self.pushButton_undo.setEnabled(False)
        self.button_check_pulse.setEnabled(False)
        self.button_normalize.setEnabled(False)

        #run code by default

        # self.button_read_pulse.click()


        # self.pushButton_reset.setEnabled(False)
        # self.pushButton_plot.setEnabled(False)
        # self.pushButton_zoom.setEnabled(False)

    # ------------------------
    def load_pickle(self):
        logging.info('loading pulse data')
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
            self.KG1_data = pickle.load(f)
        f.close()
        logging.info('data loaded')

    # ------------------------
    def save_to_pickle(self):
        logging.info('saving pulse data')
        with open('./saved/' + str(self.pulse) + '.pkl', 'wb') as f:
            pickle.dump(
                [self.pulse, self.KG1_data,
                 self.KG4_data, self.MAG_data, self.PELLETS_data,
                 self.ELM_data, self.HRTS_data,
                 self.NBI_data, self.is_dis, self.dis_time,
                 self.LIDAR_data], f)
        f.close()
        logging.info('data saved')

    # ------------------------
    def save_kg1(self):
        logging.info('saving KG1 data')
        with open('./saved/' + str(self.pulse) + '_kg1.pkl', 'wb') as f:
            pickle.dump(self.KG1_data,f)
        f.close()
        logging.info('kg1 data saved')



    def handle_zoombutton(self):
        pass

# ------------------------
    def handle_resetbutton(self):
        pass

# ------------------------
    def handle_readbutton(self):

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

        self.widget_LID_ALL.figure.clear()
        self.widget_LID_ALL.draw()

        self.widget_MIR.figure.clear()
        self.widget_MIR.draw()

        ax1 = self.widget_LID1.figure.add_subplot(111)

        ax2 = self.widget_LID2.figure.add_subplot(111)
        ax3 = self.widget_LID3.figure.add_subplot(111)
        ax4 = self.widget_LID4.figure.add_subplot(111)

        ax5 = self.widget_LID5.figure.add_subplot(211)
        ax51 = self.widget_LID5.figure.add_subplot(212)

        ax6 = self.widget_LID6.figure.add_subplot(211)
        ax61 = self.widget_LID6.figure.add_subplot(212)

        ax7 = self.widget_LID7.figure.add_subplot(211)
        ax71 = self.widget_LID7.figure.add_subplot(212)

        ax8 = self.widget_LID8.figure.add_subplot(211)
        ax81 = self.widget_LID8.figure.add_subplot(212)

        ax_all = self.widget_LID_ALL.figure.add_subplot(111)

        ax_mir = self.widget_MIR.figure.add_subplot(111)

        self.ax1 = ax1
        self.ax1 = ax2
        self.ax1 = ax3
        self.ax1 = ax4
        self.ax1 = ax5
        self.ax1 = ax6
        self.ax1 = ax7
        self.ax1 = ax8

        self.ax51 = ax51
        self.ax61 = ax61
        self.ax71 = ax71
        self.ax81 = ax81

        self.ax_all = ax_all
        self.ax_mir = ax_mir



        # read pulse number
        self.pulse = int(self.lineEdit_jpn.text())
        logger.info("Reading data for pulse {}".format(str(self.pulse)))

        # -------------------------------
        # 0. Read in KG1 variables and config data.
        # -------------------------------
        # Read in signal names and configuration data





        exists = os.path.isfile('./saved/'+str(self.pulse)+'.pkl')


        if exists:
            if  (self.checkBox_newpulse.isChecked() == False):

                logging.info('pulse data already downloaded')
                self.load_pickle()
            else:
                logging.info('pulse data already downloaded - you are requesting to download again')
                self.areyousure_window = QtGui.QMainWindow()
                self.ui_areyousure = Ui_areyousure_window()
                self.ui_areyousure.setupUi(self.areyousure_window)
                self.areyousure_window.show()

                self.ui_areyousure.pushButton_YES.clicked.connect(self.handle_yes)
                self.ui_areyousure.pushButton_NO.clicked.connect(self.handle_no)
        else:
            self.readdata()





        # self.button_plot.setEnabled(True)
        self.button_check_pulse.setEnabled(True)
        self.button_save.setEnabled(True)
        self.button_normalize.setEnabled(True)
        self.pushButton_apply.setEnabled(True)
        self.pushButton_makeperm.setEnabled(True)
        self.pushButton_undo.setEnabled(True)


        for chan in self.KG1_data.density.keys():
            ax_name=  'ax'+str(chan)
            name='LID'+str(chan)
            widget_name='widget_LID'+str(chan)
            vars()[ax_name].plot(self.KG1_data.density[chan].time, self.KG1_data.density[chan].data,label=name,marker='x', color='b')
            vars()[ax_name].legend()
            self.ax_all.plot(self.KG1_data.density[chan].time, self.KG1_data.density[chan].data,label=name,marker='x')
            self.ax_all.legend()
            # exec(
            #     'self.' + ax_name + '.plot(KG1_data.density[chan].time, KG1_data.density[chan].data)')
            # self.ax_all.plot(KG1_data.density[chan].time, KG1_data.density[chan].data)

            # draw_widget(chan)
            self.widget_LID1.draw()

            if chan >4:
                name1='MIR'+str(chan)
                ax_name1 = 'ax' + str(chan)+str(1)
                widget_name1 = 'widget_LID' + str(chan)+str(1)
                # vars()[ax_name].plot(kg1_data.density[chan].time,
                #                      kg1_data.density[chan].data,'b',label=name,,marker='x')
                # # exec('self.'+ax_name1+'.plot(KG1_data.density[chan].time,KG1_data.density[chan].data,''bx'')')
                # # draw_widget(chan)
                # exec(
                #     'self.' + ax_name1 + '.plot(KG1_data.vibration[chan].time,KG1_data.vibration[chan].data)')
                vars()[ax_name1].plot(self.KG1_data.vibration[chan].time,
                                      self.KG1_data.vibration[chan].data,marker='x',label=name1, color='b')
                vars()[ax_name1].legend()
                self.ax_mir.plot(self.KG1_data.vibration[chan].time,
                                 self.KG1_data.vibration[chan].data,marker='x',label=name1)
                self.ax_mir.legend()
                # draw_widget(chan)

        # plt.show()
        #
        # a=[x for x in range(10)]
        # b=np.square(a)
        # ax1.plot(a,b,'r')
        # self.widget_LID1.draw()
        # ax2.plot(a,b,'b')
        # self.widget_LID2.draw()
        # ax3.plot(a,b,'k')

        # plt.figure()
        # chan = 1
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

        # self.widget_LID_ALL.figure.clear()
        self.widget_LID_ALL.draw()

        # self.widget_MIR.figure.clear()
        self.widget_MIR.draw()

    # ----------------------------
    def handle_no(self):
        """
        functions that ask to confirm if user wants NOT to proceed

        to set read data for selected pulse
    """


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
        logging.debug('pressed %s button',
                      self.ui_areyousure.pushButton_YES.text())
        logging.debug('continue')
        self.readdata()


        self.ui_areyousure.pushButton_YES.setChecked(False)

        self.areyousure_window.hide()

# -----------------------
    def readdata(self):




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

        read_uid = self.comboBox_readuid.currentText()

        success = KG1_data.read_data(self.pulse, read_uid=read_uid)

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
        self.dis_time = dis_time
        logger.info("Time of disruption {}".format(dis_time))

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

        # save data to pickle
        self.save_to_pickle()
        # save KG1 data on different file (needed later when applying corrections)
        self.save_kg1()

    # ------------------------
    def plot_2nd_trace(self):
            # self.s2ndtrace = self.comboBox_2ndtrace.itemText(i)
            self.s2ndtrace = self.comboBox_2ndtrace.currentText()

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

            ax1 = self.widget_LID1.figure.add_subplot(111)

            ax2 = self.widget_LID2.figure.add_subplot(111)
            ax3 = self.widget_LID3.figure.add_subplot(111)
            ax4 = self.widget_LID4.figure.add_subplot(111)

            ax5 = self.widget_LID5.figure.add_subplot(211)
            ax51 = self.widget_LID5.figure.add_subplot(212)

            ax6 = self.widget_LID6.figure.add_subplot(211)
            ax61 = self.widget_LID6.figure.add_subplot(212)

            ax7 = self.widget_LID7.figure.add_subplot(211)
            ax71 = self.widget_LID7.figure.add_subplot(212)

            ax8 = self.widget_LID8.figure.add_subplot(211)
            ax81 = self.widget_LID8.figure.add_subplot(212)

            ax_all = self.widget_LID_ALL.figure.add_subplot(111)

            ax_mir = self.widget_MIR.figure.add_subplot(111)

            for chan in self.KG1_data.density.keys():
                ax_name = 'ax' + str(chan)
                name = 'LID' + str(chan)
                widget_name = 'widget_LID' + str(chan)
                vars()[ax_name].plot(self.KG1_data.density[chan].time,
                                     self.KG1_data.density[chan].data,
                                     label=name, marker='x', color='b')
                vars()[ax_name].legend()
                # self.ax_all.plot(self.KG1_data.density[chan].time, self.KG1_data.density[chan].data,label=name,marker='x')
                # self.ax_all.legend()
                # exec(
                #     'self.' + ax_name + '.plot(KG1_data.density[chan].time, KG1_data.density[chan].data)')
                # self.ax_all.plot(KG1_data.density[chan].time, KG1_data.density[chan].data)

                # draw_widget(chan)
                self.widget_LID1.draw()

                if chan > 4:
                    name1 = 'MIR' + str(chan)
                    ax_name1 = 'ax' + str(chan) + str(1)
                    widget_name1 = 'widget_LID' + str(chan) + str(1)
                    # vars()[ax_name].plot(kg1_data.density[chan].time,
                    #                      kg1_data.density[chan].data,'b',label=name,,marker='x')
                    # # exec('self.'+ax_name1+'.plot(KG1_data.density[chan].time,KG1_data.density[chan].data,''bx'')')
                    # # draw_widget(chan)
                    # exec(
                    #     'self.' + ax_name1 + '.plot(KG1_data.vibration[chan].time,KG1_data.vibration[chan].data)')
                    vars()[ax_name1].plot(self.KG1_data.vibration[chan].time,
                                          self.KG1_data.vibration[chan].data,
                                          marker='x', label=name1, color='b')
                    vars()[ax_name1].legend()
                    # self.ax_mir.plot(self.KG1_data.vibration[chan].time,
                    #                  self.KG1_data.vibration[chan].data,marker='x',label=name1)
                    # self.ax_mir.legend()
                    # draw_widget(chan)

            logging.info('plotting second trace {}'.format(self.s2ndtrace))
            if self.s2ndtrace == None:
                logging.info('no second trace selected')
            if self.s2ndtrace == 'HRTS':
                # if len(self.HRTS_data.density[chan].time) == 0:
                #     logging.info('NO HRTS data')
                # else:
                    for chan in self.HRTS_data.density.keys():
                        ax_name = 'ax' + str(chan)
                        name = 'HRTS ch.' + str(chan)
                        widget_name = 'widget_LID' + str(chan)

                        vars()[ax_name].plot(self.HRTS_data.density[chan].time,
                                             self.HRTS_data.density[chan].data,
                                             label=name, marker='o',
                                             color='orange')

                        if chan > 4:
                            ax_name1 = 'ax' + str(chan) + str(1)
                            widget_name1 = 'widget_LID' + str(chan) + str(1)
                            vars()[ax_name].plot(
                                self.HRTS_data.density[chan].time,
                                self.HRTS_data.density[chan].data, label=name,
                                marker='o', color='orange')

            if self.s2ndtrace == 'Lidar':
                if len(self.LIDAR_data.density[chan].time) == 0:
                    logging.info('NO LIDAR data')
                else:

                    for chan in self.KG1_data.constants.kg1v.keys():
                        ax_name = 'ax' + str(chan)
                        name = 'HRTS ch.' + str(chan)
                        widget_name = 'widget_LID' + str(chan)

                        vars()[ax_name].plot(self.LIDAR_data.density[chan].time,
                                             self.LIDAR_data.density[chan].data,
                                             label=name, marker='o',
                                             color='green')

                        if chan > 4:
                            ax_name1 = 'ax' + str(chan) + str(1)
                            widget_name1 = 'widget_LID' + str(chan) + str(1)
                            vars()[ax_name].plot(
                                self.LIDAR_data.density[chan].time,
                                self.LIDAR_data.density[chan].data, label=name,
                                marker='o', color='green')

            if self.s2ndtrace == 'Far':
                # if len(self.KG4_data.faraday[chan].time) == 0:
                #     logging.info('NO Far data')
                # else:

                for chan in self.KG4_data.faraday.keys():
                    ax_name = 'ax' + str(chan)
                    name = 'Far ch.' + str(chan)
                    widget_name = 'widget_LID' + str(chan)

                    vars()[ax_name].plot(self.KG4_data.faraday[chan].time,
                                         self.KG4_data.faraday[chan].data,
                                         label=name, marker='o', color='red')

                    if chan > 4:
                        ax_name1 = 'ax' + str(chan) + str(1)
                        widget_name1 = 'widget_LID' + str(chan) + str(1)
                        vars()[ax_name].plot(self.KG4_data.faraday[chan].time,
                                             self.KG4_data.faraday[chan].data,
                                             label=name, marker='o',
                                             color='red')

            if self.s2ndtrace == 'CM':

                # if len(self.KG4_data.xg_ell_signal[chan].time) == 0:
                #     logging.info('NO CM data')
                # else:

                for chan in self.KG4_data.xg_ell_signal.keys():
                    ax_name = 'ax' + str(chan)
                    name = 'CM ch.' + str(chan)
                    widget_name = 'widget_LID' + str(chan)

                    vars()[ax_name].plot(self.KG4_data.xg_ell_signal[chan].time,
                                         self.KG4_data.xg_ell_signal[chan].data,
                                         label=name, marker='o', color='purple')

                    if chan > 4:
                        ax_name1 = 'ax' + str(chan) + str(1)
                        widget_name1 = 'widget_LID' + str(chan) + str(1)
                        vars()[ax_name].plot(
                            self.KG4_data.xg_ell_signal[chan].time,
                            self.KG4_data.xg_ell_signal[chan].data, label=name,
                            marker='o', color='purple')

            if self.s2ndtrace == 'KG1_RT':
                # if len(self.KG4_data.density[chan].time) == 0:
                #     logging.info('NO KG1_RT data')
                # else:

                for chan in self.KG4_data.density.keys():
                    ax_name = 'ax' + str(chan)
                    name = 'KG1 RT ch.' + str(chan)
                    widget_name = 'widget_LID' + str(chan)

                    vars()[ax_name].plot(self.KG1_data.kg1rt[chan].time,
                                         self.KG1_data.kg1rt[chan].data,
                                         label=name, marker='o', color='brown')

                    if chan > 4:
                        ax_name1 = 'ax' + str(chan) + str(1)
                        widget_name1 = 'widget_LID' + str(chan) + str(1)
                        vars()[ax_name].plot(self.KG1_data.kg1rt[chan].time,
                                             self.KG1_data.kg1rt[chan].data,
                                             label=name, marker='o',
                                             color='brown')

            if self.s2ndtrace == 'BremS':
                logging.debug('not implemented yet')

                # for chan in self.LIDAR_data.constants.kg1v.keys():
                #     ax_name = 'ax' + str(chan)
                #     name = 'HRTS ch.' + str(chan)
                #     widget_name = 'widget_LID' + str(chan)
                #
                #     vars()[ax_name].plot(self.LIDAR_data.density[chan].time,
                #                          self.LIDAR_data.density[chan].data,label=name,marker='o', color='r')
                #
                #     self.widget_LID1.draw()
                #
                #
                #     if chan > 4:
                #         ax_name1 = 'ax' + str(chan) + str(1)
                #         widget_name1 = 'widget_LID' + str(chan) + str(1)
                #         vars()[ax_name].plot(self.LIDAR_data.density[chan].time,
                #                              self.LIDAR_data.density[chan].data,label=name,marker='o', color='r')

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
    def plot_markers(self):
        # self.s2ndtrace = self.comboBox_2ndtrace.itemText(i)
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

        ax1 = self.widget_LID1.figure.add_subplot(111)

        ax2 = self.widget_LID2.figure.add_subplot(111)
        ax3 = self.widget_LID3.figure.add_subplot(111)
        ax4 = self.widget_LID4.figure.add_subplot(111)

        ax5 = self.widget_LID5.figure.add_subplot(211)
        ax51 = self.widget_LID5.figure.add_subplot(212)

        ax6 = self.widget_LID6.figure.add_subplot(211)
        ax61 = self.widget_LID6.figure.add_subplot(212)

        ax7 = self.widget_LID7.figure.add_subplot(211)
        ax71 = self.widget_LID7.figure.add_subplot(212)

        ax8 = self.widget_LID8.figure.add_subplot(211)
        ax81 = self.widget_LID8.figure.add_subplot(212)

        ax_all = self.widget_LID_ALL.figure.add_subplot(111)

        ax_mir = self.widget_MIR.figure.add_subplot(111)

        for chan in self.KG1_data.density.keys():
            ax_name = 'ax' + str(chan)
            name = 'LID' + str(chan)
            widget_name = 'widget_LID' + str(chan)
            vars()[ax_name].plot(self.KG1_data.density[chan].time,
                                 self.KG1_data.density[chan].data,
                                 label=name, marker='x', color='b')
            vars()[ax_name].legend()
            # self.ax_all.plot(self.KG1_data.density[chan].time, self.KG1_data.density[chan].data,label=name,marker='x')
            # self.ax_all.legend()
            # exec(
            #     'self.' + ax_name + '.plot(KG1_data.density[chan].time, KG1_data.density[chan].data)')
            # self.ax_all.plot(KG1_data.density[chan].time, KG1_data.density[chan].data)

            # draw_widget(chan)
            self.widget_LID1.draw()

            if chan > 4:
                name1 = 'MIR' + str(chan)
                ax_name1 = 'ax' + str(chan) + str(1)
                widget_name1 = 'widget_LID' + str(chan) + str(1)
                # vars()[ax_name].plot(kg1_data.density[chan].time,
                #                      kg1_data.density[chan].data,'b',label=name,,marker='x')
                # # exec('self.'+ax_name1+'.plot(KG1_data.density[chan].time,KG1_data.density[chan].data,''bx'')')
                # # draw_widget(chan)
                # exec(
                #     'self.' + ax_name1 + '.plot(KG1_data.vibration[chan].time,KG1_data.vibration[chan].data)')
                vars()[ax_name1].plot(self.KG1_data.vibration[chan].time,
                                      self.KG1_data.vibration[chan].data,
                                      marker='x', label=name1, color='b')
                vars()[ax_name1].legend()
                # self.ax_mir.plot(self.KG1_data.vibration[chan].time,
                #                  self.KG1_data.vibration[chan].data,marker='x',label=name1)
                # self.ax_mir.legend()
                # draw_widget(chan)

        logging.info('plotting marker {}'.format(self.marker))
        if self.marker == None:
            logging.info('no marker selected')
        if self.marker == 'ELMs':
            for chan in self.KG1_data.density.keys():
                        ax_name = 'ax' + str(chan)
                        # name = 'HRTS ch.' + str(chan)
                        widget_name = 'widget_LID' + str(chan)

                        vars()[ax_name].plot(self.ELM_data.elms_signal.time, self.ELM_data.elms_signal.data,
                                             color='black')
                        if self.ELM_data.elm_times is not None:
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

                        # make_plot([[elms_signal.time, elms_signal.data],
                        #            [elms_signal.time, data_filt],
                        #            [elms_signal.time[0:-10], first_deriv],
                        #            [elms_signal.time, elms_signal.data],
                        #            [elms_signal.time, elms_signal.data]],
                        #           labels=["Be-II", "filt", "1st deriv",
                        #                   "starts", "ends"],
                        #           colours=["blue", "green", "green", "blue",
                        #                    "blue"],
                        #           pformat=[2, 1, 1, 1],
                        #           show=True,
                        #           vert_lines=[elm_times, [],
                        #                       elms_signal.time[ind_start],
                        #                       elms_signal.time[ind_end]],
                        #           horz_lines=[[], [self.UP_THRESH,
                        #                            self.DOWN_THRESH], [], []],
                        #           title="Be-II signal & 1st derivative used for ELM finding, detected elm times shown.")

        if self.marker == 'MAGNETICs':
            for chan in self.KG1_data.density.keys():
                ax_name = 'ax' + str(chan)
                # name = 'HRTS ch.' + str(chan)
                widget_name = 'widget_LID' + str(chan)

                if (self.MAG_data.start_ip) > 0:
                    for vert in [self.MAG_data.start_ip, self.MAG_data.end_ip]:
                        vars()[ax_name].axvline(x=vert, ymin=0, ymax=1,
                                            linewidth=2, color="red")
                    for vert in [self.MAG_data.start_flattop, self.MAG_data.end_flattop]:
                        vars()[ax_name].axvline(x=vert, ymin=0, ymax=1,
                                            linewidth=2, color="green")
                else:
                    logging.info('No MAGNETICs marker')


        if self.marker == 'NBI':
            for chan in self.KG1_data.density.keys():
                        ax_name = 'ax' + str(chan)
                        # name = 'HRTS ch.' + str(chan)
                        widget_name = 'widget_LID' + str(chan)

                        if (self.NBI_data.start_nbi) > 0.0:
                            for vert in [self.NBI_data.start_nbi, self.NBI_data.end_nbi]:
                                vars()[ax_name].axvline(x=vert, ymin=0, ymax=1,
                                                    linewidth=2, color="red")
                        else:
                            logging.info('No NBI marker')




        if self.marker == 'PELLETs':
            for chan in self.KG1_data.density.keys():
                ax_name = 'ax' + str(chan)
                # name = 'HRTS ch.' + str(chan)
                widget_name = 'widget_LID' + str(chan)

                if self.PELLETS_data.time_pellets is not None:
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
#------------------------
    def handle_checkbutton(self):
        pass

#------------------------
    def handle_savebutton(self):
        # -------------------------------
        # 13. Write data to PPF
        #     Don't allow for writing of new PPF if write UID is JETPPF and test is true.
        #     This is since with test set we can over-write manually corrected data.
        # -------------------------------
        if self.radioButton_storeData.isChecked() == True:
            logger.info("\n             Writing PPF with UID {}".format(write_uid))
            # write_status = kg1_signals.write_data(self.pulse, write_uid, mag)


            write_status = 0
            if write_status != 0:
                logger.error("There was a problem writing the PPF.")
                return sys.exit(write_status)
            else:
                logger.info("No PPF was written. UID given was {}, stats: {}".format(write_uid, test))

                logger.info("\n             Finished.")
        if self.radioButton_storeSF.isChecked() == True:
            logger.info("\n             Writing Status Flag ONLY")
            # write_status = kg1_signals.write_data(self.pulse, write_uid, mag)
            write_status = 0
            if write_status != 0:
                logger.error("There was a problem writing the PPF.")
                return sys.exit(write_status)
            else:
                logger.info("No PPF was written. UID given was {}, stats: {}".format(write_uid, test))

                logger.info("\n             Finished.")


#------------------------
    def handle_normalizebutton(self):
        pass

#------------------------
    def handle_applybutton(self):
        pass

#------------------------
    def handle_makepermbutton(self):
        pass

#------------------------
    def handle_undobutton(self):
        pass





# ----------------------------
    def handle_exit_button(self):
        """
        Exit the application
        """
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



def main():
    """
    Main function

    the only input to the GUI is the debug

    by default is set to INFO
    """
    logger.info("Running WOOP.")
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = woop()
    #MainWindow.show()
    MainWindow.showMaximized()
    app.exec_()


if __name__ == '__main__':

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

