from PyQt5.QtWidgets import QLabel
from PyQt5 import QtGui
from util import utils


class MenuItem(QLabel):
    def __init__(self):
        super().__init__()
        self.clicked = utils.clickable(self)

    def registerClickedCallback(self, cb):
        if callable(cb):
            self.clicked.connect(cb)

    def setImage(self, path):
        image = QtGui.QPixmap()
        image.load(path)
        self.setPixmap(image)
