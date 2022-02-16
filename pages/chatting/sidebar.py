import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui
from util.utils import clickable
from model.user import User
from model.user_info_dto import UserInfoDto
from pages.home.user_info_context import UserInfoContext
from ui.component.scrollpage import ScrollPage


class SidebarSignals(QtCore.QObject):
    CLOSE = QtCore.pyqtSignal()


class Sidebar(QWidget):
    user_info_context = UserInfoContext()
    chatters:list = []

    def __init__(self, parent=None):
        super(Sidebar, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.SIGNALS = SidebarSignals()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._escapezone = QWidget()
        self._escapezone.setSTyleSheet('background-color:rgba(20, 20, 20, 0.1)')
        clickable(self._escapezone).connect(self._onclose)

        self._sidebar_wrap = QWidget()
        self._sidebar_wrap.setStyleSheet('background-color: white')
        self._sidebar_wrap.setFixedWidth(250)
        self._sidebar = QVBoxLayout()
        self._sidebar.setAlignment(QtCore.Qt.AlignTop)
        self._sidebar.setContentsMargins(0, 0, 0, 0)
        # initialize sidebar
        self.me_info_widget = MyInfoWidget(self.user_info_context.getMe())
        self.chatter_scroll_widget = ScrollPage()
        self.updatePeople()
        self.footer_menu_layout = QHBoxLayout()
        self.footer_menu_layout.addWidget(QPushButton('나가기'))
        self.footer_menu_layout.addStretch(1)
        self.footer_menu_layout.addWidget(QPushButton('친구초대'))
        # place widgets
        self.sidebarAddWidget(self.me_info_widget)
        self.sidebarAddWidget(self.chatter_scroll_widget)
        self.sidebarAddLayout(self.footer_menu_layout)
        self._sidebar_wrap.setLayout(self._sidebar)

        layout.addWidget(self._escapezone)
        layout.addWidget(self._sidebar_wrap)
        self.setLayout(layout)

    def sidebarAddLayout(self, layout):
        self._sidebar.addLayout(layout)

    def sidebarAddWidget(self, widget):
        self._sidebar.addWidget(widget)

    def updateMe(self):
        self.me_info_widget.updateMe(self.user_info_context.getMe())

    def updatePeople(self):
        me_hid = self.user_info_context.getMyInfo().h_userid
        friends_hid = [info.h_userid for info in self.user_info_context.getFriendsInfo()]
        self.chatter_scroll_widget.removeAll()
        for chatter in self.chatters:
            if isinstance(chatter, UserInfoDto):
                if chatter.h_userid == me_hid:
                    continue
                if chatter.h_userid in friends_hid:
                    friends_hid.remove(chatter.h_userid)
                    self.chatter_scroll_widget.addWidget(
                        ChatUserInfoWidget(chatter, isFriend=True)
                    )
                else:
                    self.chatter_scroll_widget.addWidget(
                        ChatUserInfoWidget(chatter, isFriend=False)
                    )
    def setChatters(self, chatters:list):
        self.chatters = chatters

    def addChatter(self, chatter:UserInfoDto):
        self.chatters.append(chatter)

    def updateUI(self):
        self.updateMe()
        self.updatePeople()

    def _onclose(self):
        self.SIGNALS.CLOSE.emit()


class MyInfoWidget(QWidget):

    def __init__(self, me:User):
        super().__init__()
        self.me = me
        self.initUI()

    def initUI(self):
        self.setMaximumHeight(80)
        self.setMaximumWidth(250)

        _layout = QHBoxLayout()
        _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignCenter)

        self.icon = QWidget()
        self.icon.setFixedSize(40, 40)

        right_layout = QVBoxLayout()
        right_layout.setAlignment(QtCore.Qt.AlignTop)
        self.name_label = QLabel()
        self.name_label.setFont(QtGui.QFont('맑은 고딕', 11))
        self.position_label = QLabel()
        self.position_label.setWordWrap(True)
        self.position_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.position_label.setFont(QtGui.QFont('맑은 고딕', 9))
        right_layout.addWidget(self.name_label)
        right_layout.addWidget(self.position_label)

        self.updateMe()
        _layout.addWidget(self.icon)
        _layout.addLayout(right_layout)
        self.setLayout(_layout)

    def updateMe(self, me:User=None):
        if me:
            self.me = me
        self.icon.setStyleSheet(f'background-color:{self.me.get_color()}; border-radius:20px;')
        self.name_label.setText(self.me.get_name())
        self.position_label.setText(f'{self.me.get_department()} {self.me.get_position()}')


class ChatUserInfoWidget(QWidget):

    def __init__(self, userinfo:UserInfoDto, isFriend=True):
        super().__init__()
        self.userinfo = userinfo
        self.isFriend = isFriend
        self.initUI()

    def initUI(self):
        self.setMaximumHeight(70)
        self.setMaximumWidth(250)

        _layout = QHBoxLayout()
        _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignCenter)

        self.icon = QWidget()
        self.icon.setFixedSize(30, 30)
        self.name_label = QLabel()
        self.name_label.setFont(QtGui.QFont('맑은 고딕', 9))
        self.updateInfo()
        _layout.addWidget(self.icon)
        _layout.addSpacing(10)
        _layout.addWidget(self.name_label)
        self.setLayout(_layout)

    def updateInfo(self, userinfo:UserInfoDto=None):
        if userinfo:
            self.userinfo = userinfo
        self.icon.setStyleSheet(f'background-color:{self.userinfo.color}; border-radius:15px')
        self.name_label.setText(self.userinfo.name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # test code
    me = User()
    me.set_name('홍길동')
    me.set_department('기획팀')
    me.set_position('대리')
    myWidget = MyInfoWidget(me)
    myWidget.show()
    friend = UserInfoDto()
    friend.color = 'skyblue'
    friend.name = '김철수'
    friend.department = '홍보팀'
    friend.position = '부장'
    friendWidget = ChatUserInfoWidget(friend)
    friendWidget.show()
    sys.exit(app.exec_())
