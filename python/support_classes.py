# ----------------------------
__author__ = "B. Viola"
# ----------------------------

from matplotlib import pyplot as plt
import pdb
from canvas import Canvas
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
import logging
from matplotlib.ticker import AutoLocator

logger = logging.getLogger(__name__)

class MyLocator(AutoLocator):
    def view_limits(self, vmin, vmax):
        multiplier = 5.0
        vmin = multiplier * np.floor(vmin / multiplier)
        vmax = multiplier * np.ceil(vmax / multiplier)
        return vmin, vmax

class LineEdit(QLineEdit):
    """
    inherit from QLineEdit
    we use super so that child classes that may be using cooperative multiple inheritance will call the correct next parent class function in the Method Resolution Order (MRO).

    uses mouse press event and emit signal when clicked


    """

    signal_evoke_kb = pyqtSignal()

    def __init__(self):
        super(LineEdit, self).__init__()

    def mousePressEvent(self, QMouseEvent):
        super(LineEdit, self).mousePressEvent(QMouseEvent)
        self.signal_evoke_kb.emit()

class Key(QPushButton):

    def __init__(self, name, event, receiver):
        super(Key, self).__init__()
        self.name = name
        self.event = event
        self.setText(name)


class KeyBoard(QWidget):
    """
    Keyboard class is a new widget that pops up when the QlineEdit is clicked
    to show keys that can be pressed to write in the QlineEdit defining the corrections the users wants to apply
    """
    apply_pressed_signal = pyqtSignal()

    def __init__(self, receiver):
        super(KeyBoard, self).__init__()

        # QtGui.QWidget.__init__(self, parent)
        self.setWindowFlags(self.windowFlags() | Qt.Dialog)

        # self.resize(400, 300)
        self.move(200, 150)

        self.setWindowTitle("CHOOSE CORRECTION")
        self.receiver = receiver
        self.layout = QHBoxLayout()
        self.keys = ['-',',','0','1','2','3','4','5','APPLY']
        self.dict_keys ={'-':Qt.Key_Minus,',':Qt.Key_Comma,'0':Qt.Key_0,'1':Qt.Key_1,'2':Qt.Key_2,'3':Qt.Key_3,'4':Qt.Key_4,'5':Qt.Key_5,'APPLY':Qt.Key_Enter}
        for key in self.keys:
            key_keyboard = Key(key,self.dict_keys[key],receiver)
            if key == 'APPLY':
                key_keyboard.clicked.connect(self.apply_pressed)
            else:
                key_keyboard.clicked.connect(self.key_pressed)


            self.layout.addWidget(key_keyboard)
        self.setLayout(self.layout)

    def key_pressed(self):
        try:
            event = QKeyEvent(QEvent.KeyPress, self.sender().event, Qt.NoModifier,
                              self.sender().name, False)
            QCoreApplication.postEvent(self.receiver, event)
        except Exception as e:
            logger.log(5,e)

    def apply_pressed(self):
        # logger.log(5,self.sender().name)
        try:
            event = QKeyEvent(QEvent.KeyPress, self.sender().event, Qt.NoModifier,
                              self.sender().name, False)
            QCoreApplication.postEvent(self.receiver, event)
            self.apply_pressed_signal.emit()
            self.hide()

        except Exception as e:
            logger.log(5,e)

    def keyPressEvent(self, evt):
        event = QKeyEvent(QEvent.KeyPress, evt.key(), evt.modifiers(),
                          evt.text(), False)
        QCoreApplication.postEvent(self.receiver, event)
        evt.ignore()

# class Widget(Canvas):
#       def __init__(self,tab,chan,):
#
#             super(Widget, self).__init__()
#             self.setLayout(QtGui.QVBoxLayout())
#             self.layout().setContentsMargins(0, 710, 50,
#                                                -0)  # (left, top, right, bottom)
#             self.layout().setSpacing(0)
#             toolbar = NavigationToolbar(widget, self)
#             self.layout().addWidget(toolbar)

