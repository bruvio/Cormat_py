# ----------------------------
__author__ = "B. Viola"
# ----------------------------

import logging
from PyQt4 import QtCore, QtGui


class CustomFormatter(logging.Formatter):
    FORMATS = {
        logging.ERROR: ("[%(levelname)-8s] %(message)s", QtGui.QColor("red")),
        logging.DEBUG: (
            "[%(levelname)-8s] [%(filename)s:%(lineno)d] %(message)s",
            "green",
        ),
        logging.INFO: ("[%(levelname)-8s] %(message)s", "#0000FF"),
        logging.WARNING: (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            QtGui.QColor(100, 100, 0),
        ),
    }

    def format(self, record):
        last_fmt = self._style._fmt
        opt = CustomFormatter.FORMATS.get(record.levelno)
        if opt:
            fmt, color = opt
            self._style._fmt = '<font color="{}">{}</font>'.format(
                QtGui.QColor(color).name(), fmt
            )
        res = logging.Formatter.format(self, record)
        self._style._fmt = last_fmt
        return res


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent=None):
        super().__init__()
        self.widget = QtGui.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendHtml(msg)
        # move scrollbar
        scrollbar = self.widget.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class Dialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        logTextBox = QPlainTextEditLogger()
        logging.getLogger().addHandler(logTextBox)
        logTextBox.setFormatter(CustomFormatter())
        logging.getLogger().setLevel(logging.DEBUG)

        lay = QtGui.QVBoxLayout(self)
        lay.addWidget(logTextBox.widget)

        QtCore.QTimer(self, interval=500, timeout=self.on_timeout).start()

    @QtCore.pyqtSlot()
    def on_timeout(self):
        import random

        msgs = (
            lambda: logging.debug("damn, a bug"),
            lambda: logging.info("something to remember"),
            lambda: logging.warning("that's not right"),
            lambda: logging.error("foobar"),
            lambda: logging.critical("critical :-("),
        )
        random.choice(msgs)()


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    w = Dialog()
    w.resize(640, 480)
    w.show()
    sys.exit(app.exec_())
