# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window_old.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.setEnabled(True)
        MainWindow.resize(318, 297)
        MainWindow.setMinimumSize(QtCore.QSize(318, 297))
        MainWindow.setMaximumSize(QtCore.QSize(318, 297))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.exit_button = QtGui.QPushButton(self.centralwidget)
        self.exit_button.setGeometry(QtCore.QRect(210, 200, 75, 25))
        self.exit_button.setToolTip(_fromUtf8(""))
        self.exit_button.setWhatsThis(_fromUtf8(""))
        self.exit_button.setObjectName(_fromUtf8("exit_button"))
        self.title = QtGui.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(100, 10, 171, 22))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Verdana"))
        font.setPointSize(14)
        self.title.setFont(font)
        self.title.setObjectName(_fromUtf8("title"))
        self.layoutWidget = QtGui.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 40, 101, 151))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.edge2d_button = QtGui.QPushButton(self.layoutWidget)
        self.edge2d_button.setToolTip(_fromUtf8(""))
        self.edge2d_button.setWhatsThis(_fromUtf8(""))
        self.edge2d_button.setObjectName(_fromUtf8("edge2d_button"))
        self.verticalLayout.addWidget(self.edge2d_button)
        self.magsurf_button = QtGui.QPushButton(self.layoutWidget)
        self.magsurf_button.setToolTip(_fromUtf8(""))
        self.magsurf_button.setWhatsThis(_fromUtf8(""))
        self.magsurf_button.setObjectName(_fromUtf8("magsurf_button"))
        self.verticalLayout.addWidget(self.magsurf_button)
        self.eqdsk_button = QtGui.QPushButton(self.layoutWidget)
        self.eqdsk_button.setToolTip(_fromUtf8(""))
        self.eqdsk_button.setWhatsThis(_fromUtf8(""))
        self.eqdsk_button.setObjectName(_fromUtf8("eqdsk_button"))
        self.verticalLayout.addWidget(self.eqdsk_button)
        self.readdata_button = QtGui.QPushButton(self.layoutWidget)
        self.readdata_button.setToolTip(_fromUtf8(""))
        self.readdata_button.setWhatsThis(_fromUtf8(""))
        self.readdata_button.setObjectName(_fromUtf8("readdata_button"))
        self.verticalLayout.addWidget(self.readdata_button)
        self.title_2 = QtGui.QLabel(self.centralwidget)
        self.title_2.setGeometry(QtCore.QRect(120, 230, 201, 22))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Verdana"))
        font.setPointSize(6)
        font.setBold(True)
        font.setWeight(75)
        self.title_2.setFont(font)
        self.title_2.setObjectName(_fromUtf8("title_2"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 318, 20))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionHelp = QtGui.QAction(MainWindow)
        self.actionHelp.setObjectName(_fromUtf8("actionHelp"))
        self.actionOpen_PDF_guide = QtGui.QAction(MainWindow)
        self.actionOpen_PDF_guide.setObjectName(_fromUtf8("actionOpen_PDF_guide"))
        self.menuHelp.addAction(self.actionHelp)
        self.menuHelp.addAction(self.actionOpen_PDF_guide)
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "bruvio tools", None))
        self.exit_button.setText(_translate("MainWindow", "Exit", None))
        self.title.setText(_translate("MainWindow", "bruvio tools", None))
        self.edge2d_button.setText(_translate("MainWindow", "Edge2d", None))
        self.magsurf_button.setText(_translate("MainWindow", "MagSurf", None))
        self.eqdsk_button.setText(_translate("MainWindow", "EQDSK", None))
        self.readdata_button.setText(_translate("MainWindow", "plot data", None))
        self.title_2.setText(_translate("MainWindow", "by Bruno Viola (bruno.viola@ukaea.uk)", None))
        self.menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.actionHelp.setText(_translate("MainWindow", "Help", None))
        self.actionOpen_PDF_guide.setText(_translate("MainWindow", "Open PDF guide", None))

