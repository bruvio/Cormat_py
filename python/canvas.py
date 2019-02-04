from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
# from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar

from PyQt4 import QtGui

# ----------------------------
__author__ = "B. Viola"
# ----------------------------

class Canvas(FigureCanvas):
    def __init__(self, parent=None):
        self.figure = plt.figure()
        FigureCanvas.__init__(self, self.figure)
        FigureCanvas.setSizePolicy( self, QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding )
        FigureCanvas.updateGeometry( self )
        self.setParent(parent)





