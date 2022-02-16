from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from model.user_info_dto import UserInfoDto


class FriendFindListItemSignal(QtCore.QObject):
    ADD = QtCore.pyqtSignal(str)


class FriendFindListItem(QWidget):
    btnclicked = None
    SIGNAL = FriendFindListItemSignal()
    info = None

    def __init__(self, info:UserInfoDto):
        super().__init__()
        self.info = info
        self.initUI()

    def initUI(self):
        self.setFixedHeight(55)

        self._profile_color = QWidget()
        self._profile_color.setFixedSize(40, 40)
        self._profile_color.setStyleSheet(f'border-radius:20px; background-color:{self.info.color};')

        self._name_label = QLabel(self.info.name)
        self._pos_label = QLabel(self.info.position)
        self.addButton = QPushButton('친구 추가')
        self.addButton.clicked.connect(self._onAddClicked)
        self.btnclicked = self.addButton.clicked

        _layout = QHBoxLayout()
        _layout.setAlignment(QtCore.Qt.AlignLeft)

        left_layout = QVBoxLayout()
        left_layout.setAlignment(QtCore.Qt.AlignCenter)
        left_layout.setContentsMargins(5, 0, 5, 0)
        left_layout.setSpacing(0)
        left_layout.addWidget(self._profile_color)

        mid_widget = QWidget()
        mid_widget.setMaximumWidth(220)
        mid_widget.setFixedHeight(46)
        mid_layout = QVBoxLayout()
        mid_layout.setAlignment(QtCore.Qt.AlignCenter)
        mid_layout.addWidget(self._name_label)
        mid_layout.addWidget(self._pos_label)
        mid_widget.setLayout(mid_layout)

        right_layout = QVBoxLayout()
        right_layout.setAlignment(QtCore.Qt.AlignCenter)
        right_layout.addWidget(self.addButton)

        _layout.addLayout(left_layout)
        _layout.addWidget(mid_widget)
        _layout.addStretch(1)
        _layout.addLayout(right_layout)
        self.setLayout(_layout)

    def _onAddClicked(self):
        self.SIGNAL.ADD.emit(self.info.h_userid)
