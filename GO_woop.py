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
from os import listdir
#  pdb.set_trace()
from consts import Consts
# from kg1_consts import Kg1Consts
from mag_data import MagData
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

# Uncomment below for terminal log messages
# logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')

# class QPlainTextEditLogger(logging.Handler):
#     def __init__(self, parent):
#         super().__init__()
#         self.widget = QtGui.QPlainTextEdit(parent)
#         self.widget.setReadOnly(True)
#
#     def emit(self, record):
#         msg = self.format(record)
#         self.widget.appendPlainText(msg)
# class QPlainTextEditLogger(logging.Handler):
#     def __init__(self, parent):
#         super().__init__()
#         self.widget = QtGui.QPlainTextEdit(parent)
#         self.widget.setReadOnly(True)
#
#     def emit(self, record):
#         msg = self.format(record)
#         self.widget.appendPlainText(msg)
#
#
# class MyDialog(QtGui.QDialog, QPlainTextEditLogger):
#     def _(self, parent=None):
#         super().__init__(parent)
#
#         logTextBox = QPlainTextEditLogger(self)
#         # You can format what is printed to text box
#         logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
#         logging.getLogger().addHandler(logTextBox)
#         # You can control the logging level
#         logging.getLogger().setLevel(logging.DEBUG)
#
#         self._button = QtGui.QPushButton(self)
#         self._button.setText('Test Me')
#
#         layout = QtGui.QVBoxLayout()
#         # Add the new logging box widget to the layout
#         layout.addWidget(logTextBox.widget)
#         layout.addWidget(self._button)
#         self.setLayout(layout)



class woop(QtGui.QMainWindow, woop.Ui_MainWindow):
    """

    Main control function for Woop GUI.



    """


    # ----------------------------
    def __init__(self, parent=None):
        """
        Setup the GUI, and connect the buttons to functions.
        """
        # log_handler = QPlainTextEditLogger( < parent
        # widget >)
        # logging.getLogger().addHandler(log_handler)

        import os
        super(woop, self).__init__(parent)
        self.setupUi(self)


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
        
        
        
        
        

        
        self.edge2dfold = str(parent.parent)+'/EDGE2D'
        if "USR" in os.environ:
            logging.debug('USR in env')
            #self.owner = os.getenv('USR')
            self.owner = os.getlogin()
        else:
                logging.debug('using getuser to authenticate')
                import getpass
                self.owner = getpass.getuser()
                
        logging.debug('this is your username {}'.format(self.owner))
        self.homefold = os.path.join(os.sep, 'u', self.owner)
        logging.debug('this is your homefold {}'.format(self.homefold))

        home = str(Path.home())

        # cwd = os.getcwd()
        # self.home = cwd
        # print(self.home)
        # print(owner)
        logging.debug('we are in %s', cwd)
        # psrint(homefold + os.sep+ folder)





        self.exit_button.clicked.connect(self.handle_exit_button)
        self.PathTranfile = None

        self.PathCatalog = '/home'
        users = []
        # users = [u for u in listdir(self.PathCatalog)]
        # users=sorted(users)
        # users.insert(0,'JETPPF')
        users.append('JETPPF')
        users.append('chain1')
        users.append(self.owner)


        # fsm = Qt.QFileSystemModel()
        # index = fsm.setRootPath(self.PathCatalog)
        # self.comboBox = Qt.QComboBox()

        # self.comboBox_readuid.setModel(fsm)
        # self.comboBox_readuid.setRootModelIndex(index)
        self.comboBox_readuid.addItems(users)
        # initpulse = pdmsht()
        initpulse = 92121
        self.lineEdit_jpn.setText(str(initpulse))



        othersignallist=['None','HRTS','Lidar','BremS','Far','CM','LIDRT']
        self.comboBox_2ndtrace.addItems(othersignallist)




        write_allowedusers = []
        write_allowedusers.append(self.owner)
        write_allowedusers.append('JETPPF')

        self.comboBox_writeuid.addItems(write_allowedusers)



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
        # self.pushButton_reset.setEnabled(False)
        # self.pushButton_plot.setEnabled(False)
        # self.pushButton_zoom.setEnabled(False)


#------------------------
    def handle_zoombutton(self):
        pass

# ------------------------
    def handle_resetbutton(self):
        pass

# ------------------------
    def handle_readbutton(self):
        # read pulse number
        self.pulse = int(self.lineEdit_jpn.text())

        # -------------------------------
        # 0. Read in KG1 variables and config data.
        # -------------------------------
        # Read in signal names and configuration data



        logger.info("Reading in constants.")
        try:
            constants = Consts("consts.ini", __version__)
            # constants = Kg1Consts("kg1_consts.ini", __version__)
        except KeyError:
            logger.error("Could not read in configuration file kg1_consts.ini")
            sys.exit(65)

        logger.info("Reading data for pulse {}".format(str(self.pulse)))

        # -------------------------------
        # 1. Read in Magnetics data
        # -------------------------------
        logger.info("\n             Reading in magnetics data.")
        mag = MagData(constants)
        success = mag.read_data(self.pulse)


        # -------------------------------
        # 2. Read in KG1 data
        # -------------------------------
        logger.info("\n             Reading in KG1 data.")
        kg1_data = Kg1PPFData(constants,self.pulse)

        read_uid = self.comboBox_readuid.currentText()

        success = kg1_data.read_data(self.pulse, read_uid=read_uid)

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
        kg4_data = Kg4Data(constants)
        kg4_data.read_data(mag, self.pulse)
        # pdb.set_trace()

        # -------------------------------
        # 5. Read in pellet signals
        # -------------------------------
        logger.info("\n             Reading in pellet data.")
        pellets = PelletData(constants)
        pellets.read_data(self.pulse)

        # -------------------------------
        # 6. Read in NBI data.
        # -------------------------------
        logger.info("\n             Reading in NBI data.")
        NBI_data = NBIData(constants)
        NBI_data.read_data(self.pulse)

        # -------------------------------
        # 7. Check for a disruption, and set status flag near the disruption to 4
        #    If there was no disruption then dis_time elements are set to -1.
        #    dis_time is a 2 element list, being the window around the disruption.
        #    Within this time window the code will not make corrections.
        # -------------------------------
        logger.info("\n             Find disruption.")
        is_dis, dis_time = find_disruption(self.pulse, constants, kg1_data)
        logger.info("Time of disruption {}".format(dis_time))

        # -------------------------------
        # 8. Read in Be-II signals, and find ELMs
        # -------------------------------
        logger.info("\n             Reading in ELMs data.")
        elms = ElmsData(constants, self.pulse, dis_time=dis_time[0])
        # -------------------------------
        # 9. Read HRTS data
        # # -------------------------------
        # logger.info("\n             Reading in HRTS data.")
        # HRTS_data = HRTSData(constants)
        # HRTS_data.read_data(self.pulse)
        # # # # -------------------------------
        # # # 10. Read LIDAR data
        # # # -------------------------------
        # logger.info("\n             Reading in LIDAR data.")
        # LIDAR_data = LIDARData(constants)
        # LIDAR_data.read_data(self.pulse)
        # #










        # self.button_plot.setEnabled(True)
        self.button_check_pulse.setEnabled(True)
        self.button_save.setEnabled(True)
        self.button_normalize.setEnabled(True)
        self.pushButton_apply.setEnabled(True)
        self.pushButton_makeperm.setEnabled(True)
        self.pushButton_undo.setEnabled(True)

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

        # ax1.plot()
        # ax2.plot()
        # ax3.plot()
        # ax4.plot()
        # ax5.plot()
        # ax6.plot()
        # ax7.plot()
        # ax8.plot()
        #
        # ax51.plot()
        # ax61.plot()
        # ax71.plot()
        # ax81.plot()


        for chan in kg1_data.constants.kg1v.keys():
            ax_name =  'ax'+str(chan)
            widget_name='widget_LID'+str(chan)

            vars()[ax_name].plot(kg1_data.density[chan].time, kg1_data.density[chan].data)
            # draw_widget(chan)
            self.widget_LID1.draw()

            if chan >4:
                ax_name1 = 'ax' + str(chan)+str(1)
                widget_name1 = 'widget_LID' + str(chan)+str(1)
                vars()[ax_name].plot(kg1_data.density[chan].time,
                                     kg1_data.density[chan].data)
                # draw_widget(chan)


                vars()[ax_name1].plot(kg1_data.vibration[chan].time,
                                     kg1_data.vibration[chan].data)

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
        pass

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


    # -------------------------------
    # 1. Read in KG1 variables and config data.
    # -------------------------------
    # Read in signal names and configuration data
    # logger.info("Reading in constants.")
    # try:
    #     constants = Kg1Consts("kg1_consts.ini", __version__)
    # except KeyError:
    #         logger.error("Could not read in configuration file kg1_consts.ini")
    #         sys.exit(65)
    #

    #
    #
    #     logger.info("\n             Find disruption.")
    #     is_dis, dis_time = find_disruption(self.pulse, constants, kg1_signals)
    #     logger.info("Time of disruption {}".format(dis_time))

    #
    #
    #
    #

    #
    #
    #
    #
    #
    #                     def handle_readdata_button(self):
    #                         """
    #                         opens a new windows where the user can input a list of pulses he/she wants to plot
    #
    #                         than the user can select a standard sets (a list of signal)
    #                         and then plot them
    #
    #
    #                         :return:
    #                             """
    #
    #                             logging.info('\n')
    #                             logging.info('plotting tool')
    #
    #                             self.window_plotdata = QtGui.QMainWindow()
    #                             self.ui_plotdata = Ui_plotdata_window()
    #                             self.ui_plotdata.setupUi(self.window_plotdata)
    #                             self.window_plotdata.show()
    #
    #                             initpulse = pdmsht()
    #                             initpulse2 = initpulse -1
    #
    #                             self.ui_plotdata.textEdit_pulselist.setText(str(initpulse))
    #                             # self.ui_plotdata.textEdit_colorlist.setText('black')
    #
    #                             self.ui_plotdata.selectfile.clicked.connect(self.selectstandardset)
    #
    #                             self.ui_plotdata.plotbutton.clicked.connect(self.plotdata)
    #                             self.ui_plotdata.savefigure_checkBox.setChecked(False)
    #                             self.ui_plotdata.checkBox.setChecked(False)
    #                             self.ui_plotdata.checkBox.toggled.connect(
    #                                 lambda: self.checkstateJSON(self.ui_plotdata.checkBox))
    #
    #                             self.JSONSS = '/work/bviola/Python/kg1_tools/kg1_tools_gui/standard_set/PLASMA_main_parameters_new.json'
    #                             self.JSONSSname = os.path.basename(self.JSONSS)
    #
    #                             logging.debug('default set is {}'.format(self.JSONSSname))
    #                             logging.info('select a standard set')
    #                             logging.info('\n')
    #                             logging.info('type in a list of pulses')
    #                             """
    #                             Setup the GUI, and connect the buttons to functions.
    #                             """
    #                             import os
    #                             super(bruvio_tool, self).__init__(parent)
    #                             self.setupUi(self)
    #                             logging.debug('start')
    #                             cwd = os.getcwd()
    #                             self.workfold = cwd
    #                             self.home = cwd
    #                             parent= Path(self.home)
    #                             # print(parent.parent)


    # ----------------------------
    def handle_exit_button(self):
        """
        Exit the application
        """
        logging.info('\n')
        logging.info('Exit now')
        sys.exit()


    def draw_widget(self,chan):
        if chan ==1:
            self.widget_LID1.draw()
        if chan ==2:
            self.widget_LID2.draw()
        if chan ==3:
            self.widget_LID3.draw()
        if chan ==4:
            self.widget_LID4.draw()
        if chan ==5:
            self.widget_LID5.draw()
        if chan ==6:
            self.widget_LID6.draw()
        if chan ==7:
            self.widget_LID7.draw()
        if chan ==8:
            self.widget_LID8.draw()


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
    MainWindow.show()
    # MainWindow.showMaximized()
    app.exec_()

    # app = None
    # if (not QtGui.QApplication.instance()):
    #     app = QtGui.QApplication([])
    # dlg = MyDialog()
    # dlg.show()
    # dlg.raise_()
    # if (app):
    #     app.exec_()

    # app = QtGui.QApplication(sys.argv)
    # MainWindow = QtGui.QMainWindow()
    # ui = bruvio_tool()
    # ui.setupUi(MainWindow)
    # MainWindow.show()
    # sys.exit(app.exec_())
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

