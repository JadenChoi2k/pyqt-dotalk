from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5 import QtCore
from util import utils


class MenuItemBySvgText(QWidget):
    clicked = None

    def __init__(self, svgtxt, parent=None, width=40, height=40, padding=10):
        super(MenuItemBySvgText, self).__init__(parent)
        self.svgtxt = svgtxt
        self._width = width
        self._height = height
        self._padding = padding
        self.clicked = utils.clickable(self)
        self.initUI()

    def initUI(self):
        _layout = QVBoxLayout()
        _layout.setContentsMargins(self._padding, self._padding, self._padding, self._padding)
        _layout.setAlignment(QtCore.Qt.AlignCenter)
        svgwgt = utils.createSvgFromText(self.svgtxt)
        svgwgt.setFixedSize(self._width, self._height)
        _layout.addWidget(svgwgt)
        self.setLayout(_layout)
