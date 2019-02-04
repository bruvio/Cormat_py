
import logging
from PyQt4 import Qt, QtCore,QtGui


class QPlainTextEditLogger(logging.Handler):
    """
    class that defines a handler to write logging message inside the GUI
    the geometry and position of the TextEdit is defined here, not by QT designer
    """



    def __init__(self, parent):
        super().__init__()
        #first creates a text edit widget (parent is the main gui)
        self.widget = QtGui.QPlainTextEdit(parent)
        #adding this newly created widget to gridLayout_4
        parent.gridLayout_4.addWidget(self.widget,4, 0, 1, 2)
        #self.widget.setGeometry(11,583,337,213)

        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)