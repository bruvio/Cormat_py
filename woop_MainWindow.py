# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window_woop.ui'
#
# Created: Thu Nov 29 16:38:54 2018
#      by: PyQt4 UI code generator 4.10.1
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
        MainWindow.resize(1158, 728)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.title = QtGui.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(220, 10, 171, 22))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Verdana"))
        font.setPointSize(14)
        self.title.setFont(font)
        self.title.setObjectName(_fromUtf8("title"))
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(30, 60, 145, 25))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(30, 100, 145, 25))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.pushButton_3 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(30, 160, 145, 25))
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.pushButton_4 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(30, 200, 145, 25))
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.pushButton_5 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_5.setGeometry(QtCore.QRect(30, 250, 145, 25))
        self.pushButton_5.setObjectName(_fromUtf8("pushButton_5"))
        self.pushButton_6 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_6.setGeometry(QtCore.QRect(30, 290, 145, 25))
        self.pushButton_6.setObjectName(_fromUtf8("pushButton_6"))
        self.pushButton_7 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_7.setGeometry(QtCore.QRect(30, 350, 84, 25))
        self.pushButton_7.setObjectName(_fromUtf8("pushButton_7"))
        self.comboBox_Machine = QtGui.QComboBox(self.centralwidget)
        self.comboBox_Machine.setGeometry(QtCore.QRect(240, 60, 120, 25))
        self.comboBox_Machine.setEditable(True)
        self.comboBox_Machine.setObjectName(_fromUtf8("comboBox_Machine"))
        self.comboBox_Machine_2 = QtGui.QComboBox(self.centralwidget)
        self.comboBox_Machine_2.setGeometry(QtCore.QRect(240, 100, 120, 25))
        self.comboBox_Machine_2.setEditable(True)
        self.comboBox_Machine_2.setObjectName(_fromUtf8("comboBox_Machine_2"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(380, 60, 59, 15))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(380, 110, 59, 15))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1158, 20))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.title.setText(_translate("MainWindow", "KG1 woop", None))
        self.pushButton.setText(_translate("MainWindow", "read pulse", None))
        self.pushButton_2.setText(_translate("MainWindow", "make correction", None))
        self.pushButton_3.setText(_translate("MainWindow", "change Status Flags", None))
        self.pushButton_4.setText(_translate("MainWindow", "plot data", None))
        self.pushButton_5.setText(_translate("MainWindow", "write status flags", None))
        self.pushButton_6.setText(_translate("MainWindow", "write ppf", None))
        self.pushButton_7.setText(_translate("MainWindow", "exit", None))
        self.label.setText(_translate("MainWindow", "read uid", None))
        self.label_2.setText(_translate("MainWindow", "write uid", None))

