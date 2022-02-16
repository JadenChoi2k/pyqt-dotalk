from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout
from PyQt5 import QtCore


class ScrollPage(QWidget):
    def __init__(self, parent=None):
        super(ScrollPage, self).__init__(parent)
        self.init()

    def init(self):
        self._wrap = QWidget()
        self._scroll = QScrollArea()
        self._scroll.setStyleSheet('border-left:none; border-right:none; background-color:white')
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._layout = QVBoxLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setAlignment(QtCore.Qt.AlignTop)
        self._wrap.setLayout(self._layout)
        self._scroll.setWidget(self._wrap)
        ui_layout = QVBoxLayout()
        ui_layout.setSpacing(0)
        ui_layout.setContentsMargins(0, 0, 0, 0)
        ui_layout.addWidget(self._scroll)
        self.setLayout(ui_layout)

    def addWidget(self, widget):
        self._layout.addWidget(widget)

    def addLayout(self, layout):
        self._layout.addLayout(layout)

    def swap(self, x, y):
        size = self._layout.count()
        if x >= size or x < 0 or y >= size or y < 0 or x == y:
            return
        X = self._layout.itemAt(x).widget()
        Y = self._layout.itemAt(y).widget()
        # swap
        if X and Y:
            tmp = X
            X = Y
            Y = tmp

    def insertWidget(self, index, widget):
        self._layout.insertWidget(index, widget)

    def removeAt(self, index):
        if index < 0 or index >= self._layout.count():
            return
        item = self._layout.itemAt(index)
        widget = item.widget()
        if widget:
            widget.setParent(None)
        else:
            lyt = item.layout()
            lyt.setParent(None)
            ScrollPage._removeLayout(lyt)

    def _removeLayout(layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                ScrollPage._removeLayout(item.layout())

    def removeWidget(self, widget):
        self._layout.removeWidget(widget)

    def removeAll(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
