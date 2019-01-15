from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from PyQt4 import QtGui
class Canvas(FigureCanvas):
    def __init__(self, parent=None):
        self.figure = plt.figure()
        FigureCanvas.__init__(self, self.figure)
        FigureCanvas.setSizePolicy( self, QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding )
        FigureCanvas.updateGeometry( self )
        self.setParent(parent)
