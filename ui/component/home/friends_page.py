from PyQt5.QtWidgets import QLabel, QVBoxLayout
from PyQt5 import QtGui
from util import utils
from ui.component.scrollpage import ScrollPage
from model.user_info_dto import UserInfoDto
from pages.home.user_info_context import UserInfoContext
from ui.component.home.friend_list_item import FriendListItem


class FriendsPage(ScrollPage):
    user_info_context: UserInfoContext = None
    my_info: UserInfoDto = UserInfoDto()
    my_info_widget = None
    my_info_layout: QVBoxLayout = None
    friends: list = None
    friends_widgets: list = None
    friends_layout: QVBoxLayout = None

    def __init__(self, parent=None):
        super(FriendsPage, self).__init__(parent)
        self.initUI()
        self.user_info_context = UserInfoContext()
        self.user_info_context.SIGNALS.UPDATE.connect(self.updateUI)
        self.user_info_context.initInfo()

    def setMyInfo(self, info:UserInfoDto):
        self.my_info = info
        if self.my_info_widget:
            self.my_info_widget.setMember(self.my_info)

    def setMyInfoLayout(self):
        self.my_info_layout = QVBoxLayout()
        me_label = QLabel('나')
        me_label.setFont(QtGui.QFont('맑은 고딕', 12))
        me_label.setContentsMargins(5, 2, 2, 0)
        self.my_info_layout.addWidget(me_label)
        self.my_info_widget = FriendListItem(self.my_info)
        utils.clickable(self.my_info_widget).connect(lambda : print('coming soon...'))
        self.my_info_layout.addWidget(self.my_info_widget)
        self.addLayout(self.my_info_layout)

    def setFriends(self, infoes:list):
        self.friends = infoes

    def setFriendsLayout(self):
        friends_layout = QVBoxLayout()
        friend_label = QLabel('친구')
        friend_label.setFont(QtGui.QFont('맑은 고딕', 12))
        friend_label.setCOntentsMargins(5, 0, 2, 2)
        friends_layout.addWidget(friend_label)
        if isinstance(self.friends, list):
            for friend in self.friends:
                friend_widget = FriendListItem(friend)
                friends_layout.addWidget(friend_widget)
        self.friends_layout = friends_layout

    def appendFriend(self, info:UserInfoDto):
        if self.friends is None:
            self.friends = []
            self.friends_widgets = []
        self.friends_append(info)
        self.friends_widgets.append(FriendListItem(info))
        self.friends_layout.addWidget(self.friends_widgets[-1])

    def updateFriends(self):
        self.removeAt(1)
        self.setFriendsLayout()
        self.addLayout(self.friends_layout)

    def updateUI(self):
        self.setMyInfo(self.user_info_context.getMyInfo())
        self.setFriends(self.user_info_context.getFriendsInfo())
        self.updateFriends()

    def initUI(self):
        self.setMyInfoLayout()
        self.setFriendsLayout()
        self.addLayout(self.my_info_layout)
        self.addLayout(self.friends_layout)
