from PyQt5.QtWidgets import QFrame
from PyQt5 import QtGui


class HLine(QFrame):
    def __init__(self, parent=None, color=QtGui.QColor('black')):
        super(HLine, self).__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(0)
        self.setMidLineWidth(3)
        self.setContentsMargins(0, 0, 0, 0)
        self.setColor(color)

    def setColor(self, color):
        pal = self.palette()
        pal.setColor(QtGui.QPalette.WindowText, color)
        self.setPalette(pal)
