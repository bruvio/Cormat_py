# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'areyousure.ui'
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

class Ui_areyousure_window(object):
    def setupUi(self, areyousure_window):
        areyousure_window.setObjectName(_fromUtf8("areyousure_window"))
        areyousure_window.resize(324, 152)
        areyousure_window.setMinimumSize(QtCore.QSize(324, 152))
        areyousure_window.setMaximumSize(QtCore.QSize(324, 152))
        self.centralwidget = QtGui.QWidget(areyousure_window)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.pushButton_YES = QtGui.QPushButton(self.centralwidget)
        self.pushButton_YES.setGeometry(QtCore.QRect(70, 60, 84, 25))
        self.pushButton_YES.setCheckable(True)
        self.pushButton_YES.setAutoExclusive(False)
        self.pushButton_YES.setObjectName(_fromUtf8("pushButton_YES"))
        self.pushButton_NO = QtGui.QPushButton(self.centralwidget)
        self.pushButton_NO.setGeometry(QtCore.QRect(170, 60, 84, 25))
        self.pushButton_NO.setCheckable(True)
        self.pushButton_NO.setAutoExclusive(False)
        self.pushButton_NO.setObjectName(_fromUtf8("pushButton_NO"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(100, 0, 121, 51))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Verdana"))
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        areyousure_window.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(areyousure_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 324, 20))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        areyousure_window.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(areyousure_window)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        areyousure_window.setStatusBar(self.statusbar)

        self.retranslateUi(areyousure_window)
        QtCore.QMetaObject.connectSlotsByName(areyousure_window)

    def retranslateUi(self, areyousure_window):
        areyousure_window.setWindowTitle(_translate("areyousure_window", "Are you sure?", None))
        self.pushButton_YES.setText(_translate("areyousure_window", "YES", None))
        self.pushButton_NO.setText(_translate("areyousure_window", "NO", None))
        self.label_3.setText(_translate("areyousure_window", "are you sure?", None))

