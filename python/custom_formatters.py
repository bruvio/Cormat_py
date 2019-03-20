# ----------------------------
__author__ = "B. Viola"
# ----------------------------
import logging
from PyQt4 import Qt, QtCore,QtGui


# Custom formatter
class MyFormatter(logging.Formatter):
    """
    class to handle the logging formatting
    """
    # ----------------------------

    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    err_fmt = "[\033[91m%(levelname)-5s\033[0m] \033[91m%(message)s\033[0m"
    dbg_fmt = "[\033[36m%(levelname)-4s\033[0m] [\033[36m%(filename)s\033[0m:\033[36m%(lineno)d\033[0m] \033[36m%(message)s\033[0m"
    dbgplus_fmt = "[\033[92m%(levelname)-8s\033[0m] (\033[92m%(filename)s:%(lineno)d\033[0m) \033[92m%(message)s\033[0m"
    info_fmt = "[\033[94m%(levelname)-4s\033[0m] \033[94m%(message)s\033[0m"
    warn_fmt = "[\033[93m%(levelname)-7s\033[0m] \033[93m%(message)s\033[0m"

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

        elif record.levelno == logging.WARNING:
            self._style._fmt = MyFormatter.warn_fmt

        elif record.levelno == 5:
            self._style._fmt = MyFormatter.dbgplus_fmt

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result

class QPlainTextEditLogger(logging.Handler):
    """
    class that defines a handler to write logging message inside the GUI
    
    """


    def __init__(self, parent):
        super().__init__()
        #first creates a text edit widget (parent is the main gui)
        self.widget = QtGui.QPlainTextEdit(parent)
        #adding this newly created widget to gridLayout_4
        parent.gridLayout_4.addWidget(self.widget,4, 0, 1, 2)
    

        self.widget.setReadOnly(True)


    def emit(self, record):

        msg = self.format(record)
        
        self.widget.appendHtml(msg)


class HTMLFormatter(logging.Formatter):
    FORMATS = {
        logging.ERROR:   ("[%(levelname)-5s] %(message)s", QtGui.QColor("red")),
        logging.DEBUG:   ("[%(levelname)-5s] [%(filename)s:%(lineno)d] %(message)s", "green"),
        logging.INFO:    ("[%(levelname)-4s] %(message)s", "#0000FF"),
        # logging.WARNING: ('%(asctime)s - %(name)s - %(levelname)s - %(message)s', QtGui.QColor(100, 100, 0)),
        logging.WARNING: ('%(levelname)s - %(message)s', QtGui.QColor(100, 100, 0)),
        5: ('%(levelname)s - [%(filename)s:%(lineno)d] - %(message)s', QtGui.QColor(0, 100, 0))


    }


    def format( self, record ):
        last_fmt = self._style._fmt
        opt = HTMLFormatter.FORMATS.get(record.levelno)
        if opt:
            fmt, color = opt
            self._style._fmt = "<font color=\"{}\">{}</font>".format(QtGui.QColor(color).name(),fmt)
        res = logging.Formatter.format( self, record )
        self._style._fmt = last_fmt
        return res