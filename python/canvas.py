# ----------------------------
__author__ = "B. Viola"
# ----------------------------

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui
import logging
logger = logging.getLogger(__name__)

class Canvas(FigureCanvas):

    """
    CLASS used to convert widget into a matplotlib figure

    contains mouse event (right click) that returns (xs,yx) when click is in axes

    """

    signal = pyqtSignal()
    def __init__(self, parent=None):
        self.figure = plt.figure()
        FigureCanvas.__init__(self, self.figure)
        FigureCanvas.setSizePolicy( self, QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding )
        FigureCanvas.updateGeometry( self )
        self.setParent(parent)
        self.xs = {}
        self.ys = {}
        self.cid = self.figure.canvas.mpl_connect('button_press_event', self)


    def __call__(self, event):
        if event.button == 3:  # right button
            # print('click', event)
            if event.inaxes is None:
                pass
            else:
                self.xs = float(event.xdata)
                self.ys = float(event.ydata)


                logger.log(5, "(time, data) = ({},{})".format(self.xs,self.ys))
            self.signal.emit()
            
            return self.xs, self.ys

        elif event.button != 3:
            return




