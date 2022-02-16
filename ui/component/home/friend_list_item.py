from datetime import date
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5 import QtCore
from util import utils
from model.user_info_dto import UserInfoDto
from pages.info.user_info_page import UserInfoPage


class FriendListItem(QWidget):
    info: UserInfoDto = None

    def __init__(self, user_info: UserInfoDto):
        super().__init__()
        self.initUI()
        self.setMember(user_info)
        utils.clickable(self).connect(self._whenClicked)

    def initUI(self):
        self.setFixedHeight(55)
        self._profile_color = QWidget()
        self._profile_color.setFixedSize(40, 40)
        self._name_label = QLabel()
        self._comment = QLabel()
        self._comment.setWordWrap(True)

        ui_layout = QHBoxLayout()
        ui_layout.setContentsMargins(6, 6, 6, 6)
        ui_layout.addWidget(self._profile_color)

        name_layout = QHBoxLayout()
        name_layout.addSpacing(5)
        name_layout.addWidget(self._name_label)
        name_layout.addStretch(1)

        right_layout = QHBoxLayout()
        right_layout.setAlignment(QtCore.Qt.AlignTop)
        right_layout.addLayout(name_layout)
        right_layout.addWidget(self._comment)

        ui_layout.addLayout(right_layout)
        self.setLayout(ui_layout)

    def setMember(self, info: UserInfoDto):
        self.info = info
        self._profile_color.setStyleSheet(f'border-radius:20px; background-color:{info.color};')
        self._name_label.setText(info.name)
        self._comment.setText(info.comment)

    def _whenClicked(self):
        self.infopage = UserInfoPage(self.info)
        self.infopage.show()