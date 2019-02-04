
import logging
from PyQt4 import Qt, QtCore,QtGui


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