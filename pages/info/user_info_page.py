import sys
sys.path.append('../..')
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui
from pages.chatting.chatting_room_context import ChattingRoomContext
from pages.home.user_info_context import UserInfoContext
from network.database.client.db_client import DbClient
from model.user_info_dto import UserInfoDto
from util import utils
from ui.ui_const import UIConst
from preferences import SCREEN_RATIO

dbClient = DbClient()
user_info_context = UserInfoContext()


class UserInfoPage(QWidget):
    _info: UserInfoDto = None
    _isFriend = True
    _isBlocked = False

    def __init__(self, info):
        super().__init__()
        self._info = info
        self._isFriend = user_info_context.isFriend(self._info.h_userid)
        self.initUI()

    def initUI(self):
        _layout = QVBoxLayout()
        _layout.setAlignment(QtCore.Qt.AlignTop)

        top_layout = QHBoxLayout()
        top_layout.setAlignment(QtCore.Qt.AlignCenter)
        profile_color = QWidget()
        profile_color.setFixedSize(50, 50)
        profile_color.setStyleSheet(f'border-radius:25px; background-color:{self._info.color}')
        top_layout.addWidget(profile_color)

        top_bottom_layout = QHBoxLayout()
        top_bottom_layout.setAlignment(QtCore.Qt.AlignCenter)
        name_label = QLabel(self._info.name)
        top_bottom_layout.addSpacing(10)
        top_bottom_layout.addWidget(name_label)

        mid_layout = QHBoxLayout()
        mid_layout.setAlignment(QtCore.Qt.AlignCener)
        comment = QLabel(self._info.comment)
        comment.setWordWrap(True)
        comment.setMaximumWidth(300)
        mid_layout.addWidget(comment)

        bottom_top_layout = QHBoxLayout()
        bottom_top_layout.setAlignment(QtCore.Qt.AlignCenter)
        department = QLabel(self._info.department)
        position = QLabel(self._info.position)
        bottom_top_layout.addWidget(department)
        bottom_top_layout.addSpacing(5)
        bottom_top_layout.addWidget(position)

        bottom_layout = QHBoxLayout()
        bottom_layout.setAlignment(QtCore.Qt.AlignCenter)
        add_button = QPushButton()
        block_button = QPushButton()

        if self._isFriend:
            add_button.setText('1대1 채팅하기')
            add_button.clicked.connect(self._onUnblockClicked)
            if self._isBlocked:
                block_button.setText('차단해제')
                block_button.clicked.connect(self._onUnblockClicked)
            else:
                block_button.setText('차단')
                block_button.clicked.connect(self._onBlockClicked)
        else:
            add_button.setText('친구 추가')
            add_button.clicked.connect(self._onAddFriendClicked)

        bottom_layout.addWidget(add_button)
        bottom_layout.addWidget(block_button)

        _layout.addSpacing(50)
        _layout.addLayout(top_layout)
        _layout.addSpacing(20)
        _layout.addLayout(top_bottom_layout)
        _layout.addLayout(mid_layout, 1)
        _layout.addLayout(bottom_top_layout)
        _layout.addSpacing(20)
        _layout.addLayout(bottom_layout)
        _layout.addSpacing(10)

        self.setLayout(_layout)

        self.resize(250 * SCREEN_RATIO[0], 400 * SCREEN_RATIO[1])
        self.setWindowTitle('정보 - ' + self._info.name)
        self.setWindowIconText(UIConst.DOTALK_ICON)

    def _onAddFriendClicked(self):
        result = user_info_context.addFriendByHashedUserid(self._info.h_userid)
        if result:
            QMessageBox.about(self, '친구 추가', '성공')
            self = UserInfoPage(self._info)
        else:
            QMessageBox.about(self, '친구 추가', '실패')

    def _onDoChatClicked(self):
        roomid = dbClient.doChatOneRoom(self._info.h_userid)
        context = ChattingRoomContext()
        if context.isexist(roomid):
            context.openChattingRoom(roomid)
        else:
            room = dbClient.getChatRoomById(roomid)
            context.addChattingRoom(roomid)

    def _onBlockClicked(self):
        print('todo : make this')
        pass

    def _onUnblockClicked(self):
        pass


if __name__ == '__main__':
    import datetime
    app = QApplication(sys.argv)

    info = UserInfoDto()
    info.color = 'black'
    info.name = '홍길동'
    info.comment = '동해물과 백두산이 마르고 닳도록 하느님이 보우하사 우리나라 만세 무궁화 삼천리 화려강산 대한사람 대한으로 길이 보전하세'
    info.department = '부서'
    info.position = '직급'

    info_page = UserInfoPage(info)
    info_page.show()
    sys.exit(app.exec_())
