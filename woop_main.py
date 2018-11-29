#!/usr/bin/env python


# ----------------------------
__author__ = "Bruno Viola"
__Name__ = "KG1 data validation tool" 
__version__ = "0"
__release__ = "0"
__maintainer__ = "Bruno Viola"
__email__ = "bruno.viola@ukaea.uk"
 __status__ = "Testing"
#__status__ = "Production"
__credits__ = ["aboboc"]

"""
Main control function for Woop GUI.



"""


import sys
import logging
import argparse
import pdb
#  pdb.set_trace()
from kg1_consts import Kg1Consts
from kg1_data import Kg1Data





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



import matplotlib.pyplot as plt
plt.rcParams["savefig.directory"] = os.chdir(os.getcwd())

logger = logging.getLogger(__name__)

class woop_tool(QtGui.QMainWindow, woop_tool.Ui_MainWindow):
    """
    Class for running the GUI and handling events.
    
    This GUI allows the user to:
    
    
    """
    
    # ----------------------------
    def __init__(self, parent=None):
        
        
        
        
        

        
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
                logging.debug('this is edge2d fold {}'.format(self.edge2dfold))
                home = str(Path.home())
                
                # cwd = os.getcwd()
                # self.home = cwd
                # print(self.home)
                # print(owner)
                logging.debug('we are in %s', cwd)
                # psrint(homefold + os.sep+ folder)
                
                pathlib.Path(cwd + os.sep + 'figures').mkdir(parents=True,exist_ok=True)
                pathlib.Path(cwd + os.sep + 'standard_set').mkdir(parents=True,exist_ok=True)
                
                self.readdata_button.clicked.connect(self.handle_readdata_button)
                self.edge2d_button.clicked.connect(self.handle_edge2d_button)
                self.eqdsk_button.clicked.connect(self.handle_eqdsk_button)
                self.magsurf_button.clicked.connect(self.handle_magsurf_button)
                self.readdata_button.setToolTip(
                    'opens windows to read standard set to plot time traces')
                
                
                self.exit_button.clicked.connect(self.handle_exit_button)
                self.PathTranfile = None

    # -------------------------------
    # 1. Read in KG1 variables and config data.
    # -------------------------------
    # Read in signal names and configuration data
    logger.info("Reading in constants.")
    try:
        constants = Kg1Consts("kg1_consts.ini", __version__)
        except KeyError:
            logger.error("Could not read in configuration file kg1_consts.ini")
            sys.exit(65)
            
            # Set plotting level
            constants.plot_type = plot_type
            constants.make_plots = plot_level
            
            
            # -------------------------------
            # 3. Read in KG1 data
            # -------------------------------
            logger.info("\n             Reading in KG1 data.")
            kg1_signals = Kg1Data(constants,shot_no)
            success = kg1_signals.read_data(shot_no, read_uid=read_uid, ignore_ppf=test)
            
            # Exit if there were no good signals
            # If success == 1 it means that at least one channel was not available. But this shouldn't stop the rest of the code
            # from running.
            if success != 0 and success != 1:
                # success = 11: Validated PPF data is already available for all channels
                # success = 8: No good JPF data was found
                # success = 9: JPF data was bad
                sys.exit(success)
                
                # -------------------------------
                
                
                logger.info("\n             Find disruption.")
                is_dis, dis_time = find_disruption(shot_no, constants, kg1_signals)
                logger.info("Time of disruption {}".format(dis_time))    
                
                
                
                
                
                # -------------------------------
                # 13. Write data to PPF
                #     Don't allow for writing of new PPF if write UID is JETPPF and test is true.
                #     This is since with test set we can over-write manually corrected data.
                # -------------------------------
                if (write_uid != "" and not test) or (test and write_uid.upper() != "JETPPF" and write_uid != ""):
                    logger.info("\n             Writing PPF with UID {}".format(write_uid))
                    write_status = kg1_signals.write_data(shot_no, write_uid, mag, ignore_current_ppf=test,interp_kg1v=interp)
                    
                    if write_status != 0:
                        logger.error("There was a problem writing the PPF.")
                        return sys.exit(write_status)
                    else:
                        logger.info("No PPF was written. UID given was {}, stats: {}".format(write_uid, test))
                        
                        logger.info("\n             Finished.")            
                        
                        
                        
                        
                        
                        def handle_readdata_button(self):
                            """
                            opens a new windows where the user can input a list of pulses he/she wants to plot
                            
                            than the user can select a standard sets (a list of signal)
                            and then plot them
                            
                            
                            :return:
                                """
                                
                                logging.info('\n')
                                logging.info('plotting tool')
                                
                                self.window_plotdata = QtGui.QMainWindow()
                                self.ui_plotdata = Ui_plotdata_window()
                                self.ui_plotdata.setupUi(self.window_plotdata)
                                self.window_plotdata.show()
                                
                                initpulse = pdmsht()
                                initpulse2 = initpulse -1
                                
                                self.ui_plotdata.textEdit_pulselist.setText(str(initpulse))
                                # self.ui_plotdata.textEdit_colorlist.setText('black')
                                
                                self.ui_plotdata.selectfile.clicked.connect(self.selectstandardset)
                                
                                self.ui_plotdata.plotbutton.clicked.connect(self.plotdata)
                                self.ui_plotdata.savefigure_checkBox.setChecked(False)
                                self.ui_plotdata.checkBox.setChecked(False)
                                self.ui_plotdata.checkBox.toggled.connect(
                                    lambda: self.checkstateJSON(self.ui_plotdata.checkBox))
                                
                                self.JSONSS = '/work/bviola/Python/kg1_tools/kg1_tools_gui/standard_set/PLASMA_main_parameters_new.json'
                                self.JSONSSname = os.path.basename(self.JSONSS)
                                
                                logging.debug('default set is {}'.format(self.JSONSSname))
                                logging.info('select a standard set')
                                logging.info('\n')
                                logging.info('type in a list of pulses')    
                                """
                                Setup the GUI, and connect the buttons to functions.
                                """
                                import os
                                super(bruvio_tool, self).__init__(parent)
                                self.setupUi(self)
                                logging.debug('start')
                                cwd = os.getcwd()
                                self.workfold = cwd
                                self.home = cwd
                                parent= Path(self.home)
                                # print(parent.parent)                        