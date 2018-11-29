    

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