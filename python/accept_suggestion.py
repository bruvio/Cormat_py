# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'accept_suggestion.ui'
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

class Ui_suggestion_window(object):
    def setupUi(self, suggestion_window):
        suggestion_window.setObjectName(_fromUtf8("suggestion_window"))
        suggestion_window.resize(256, 158)
        self.centralwidget = QtGui.QWidget(suggestion_window)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.formLayout = QtGui.QFormLayout(self.centralwidget)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Verdana"))
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_3)
        self.pushButton_NO = QtGui.QPushButton(self.centralwidget)
        self.pushButton_NO.setCheckable(True)
        self.pushButton_NO.setAutoExclusive(False)
        self.pushButton_NO.setObjectName(_fromUtf8("pushButton_NO"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.pushButton_NO)
        self.pushButton_YES = QtGui.QPushButton(self.centralwidget)
        self.pushButton_YES.setCheckable(True)
        self.pushButton_YES.setAutoExclusive(False)
        self.pushButton_YES.setObjectName(_fromUtf8("pushButton_YES"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.pushButton_YES)
        suggestion_window.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(suggestion_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 256, 20))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        suggestion_window.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(suggestion_window)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        suggestion_window.setStatusBar(self.statusbar)

        self.retranslateUi(suggestion_window)
        QtCore.QMetaObject.connectSlotsByName(suggestion_window)

    def retranslateUi(self, suggestion_window):
        suggestion_window.setWindowTitle(_translate("suggestion_window", "Are you sure?", None))
        self.label_3.setText(_translate("suggestion_window", "accept suggestion?", None))
        self.pushButton_NO.setText(_translate("suggestion_window", "NO", None))
        self.pushButton_YES.setText(_translate("suggestion_window", "YES", None))

