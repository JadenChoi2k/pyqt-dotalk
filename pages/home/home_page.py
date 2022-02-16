import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from ui.component.scrollpage import ScrollPage
from ui.component.home.friends_page import FriendsPage
from ui.component.home.chatting_home_page import ChattingHomePage
from ui.component.home.menu_item_by_svgtxt import MenuItemBySvgText
from ui.ui_const import UIConst
from icons import svgtxt
from pages.friend.friend_find_dialog import FriendFindDialog
from preferences import SCREEN_RATIO

menues = ['사람들', '채팅', '옵션']
top_menu_icons_text = [svgtxt.getFriendPlusText(), svgtxt.getMessagePlusText(), svgtxt.getSlidersText()]


class HomePage(QWidget):
    ui_layout: QVBoxLayout = None
    header: QHBoxLayout = None
    add_friend_flag = False
    body: QStackedWidget = None
    footer:QHBoxLayout = None

    def __init__(self):
        super().__init__()
        self.initHeaderButtons()
        self.initUI()

    def initUI(self):
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Background, QtGui.QColor('white'))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        self.__createHeader()
        self.__createBody()
        self.__createFooter()

        self.ui_layout = QVBoxLayout()
        self.ui_layout.setSpacing(0)
        self.ui_layout.setContentsMargins(0, 0, 0, 0)
        self.ui_layout.addLayout(self.header)
        self.ui_layout.addLayout(self.body)
        self.ui_layout.addLayout(self.footer)

        self.setLayout(self.ui_layout)
        self.setWindowTitle('두톡')
        self.setWindowIcon(QtGui.QIcon(UIConst.DOTALK_ICON))
        self.resize(350 * SCREEN_RATIO[0], 600 * SCREEN_RATIO[1])

    def initHeaderButtons(self):
        self.top_menu_icons = [MenuItemBySvgText(svgtxt, None, 25, 25, 0) for svgtxt in top_menu_icons_text]
        self.top_menu_icons[0].clicked.connect(self._showAddFriendDialog)
        # TODO : make this
        self.top_menu_icons[0].clicked.connect(lambda : print('add chat'))
        self.top_menu_icons[0].clicked.connect(lambda : print('settings'))

    def __createHeader(self):
        self.header = QHBoxLayout()
        self.header.setSPacing(0)
        self.header.setContentsMargins(10, 10, 10, 5)

        self.header_label = QLabel(menues[0])
        self.header_label.setFont(QtGui.QFont('맑은 고딕', 18))
        self.header_search_button = MenuItemBySvgText(svgtxt.getSearchText(), width=25, height=25, padding=0)
        self.header_act_button = self.top_menu_icons[0]
        self.header.addWidget(self.header_label)
        self.header.addStretch(1)
        self.header.addWidget(self.header_act_button)
        self.header.addSpacing(15)
        self.header.addWidget(self.header_act_button)

    def __createBody(self):
        self.body = QStackedWidget()
        self.friendsPage = FriendsPage()
        self.chatPage = ChattingHomePage.fromFile()
        self.optionPage = ScrollPage(self)

        self.body.addWidget(self.friendsPage)
        self.body.addWidget(self.chatPage)
        self.body.addWidget(self.optionPage)

    def __createFooter(self):
        self.footer = QHBoxLayout()
        self.footer.setContentsMargins(0, 0, 0, 0)

        self.footer_friends_button = MenuItemBySvgText(svgtxt.getPeopleIconText())
        self.footer_friends_button.clicked.connect(lambda : self._navigatePage(0))
        self.footer_chatting_button = MenuItemBySvgText(svgtxt.getChatIconText())
        self.footer_chatting_button.clicked.connect(lambda : self._navigatePage(1))
        self.footer_option_button = MenuItemBySvgText(svgtxt.getDotsIconText())
        self.footer_chatting_button.clicked.connect(lambda : self._navigatePage(2))

        self.footer.addWidget(self.footer_friends_button)
        self.footer.addWidget(self.footer_chatting_button)
        self.footer.addWidget(self.footer_option_button)

    def _showAddFriendDialog(self):
        if self.add_friend_flag:
            return
        self.add_friend_dialog = FriendFindDialog()
        self.add_friend_dialog.SIGNALS.CLOSE.connect(self._onClosedAddFriendDialog)
        self.add_friend_dialog.show()
        self.add_friend_flag = True

    def _onClosedAddFriendDialog(self):
        self.add_friend_flag = False

    def _navigatePage(self, index):
        if (self.body.count() -1) < index:
            return
        self.header_label.setText(menues[index])
        if self.header_act_button is not self.top_menu_icons[index]:
            self.header.replaceWidget(self.header_act_button, self.top_menu_icons[index])
            self.header_act_button.setParent(None)
            self.header_act_button = self.top_menu_icons[index]
        self.body.setCurrentIndex(index)

    def close(self, event):
        self.friendsPage.close()
        self.chatPage.close()
        self.optionPage.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    homePage = HomePage()
    homePage.show()
    sys.exit(app.exec_())
