from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import QFont
from ui.component.home.friend_find_page import FriendFindPage
from network.database.client.db_client import DbClient
from ui.ui_const import UIConst
from pages.home.user_info_context import UserInfoContext
from preferences import SCREEN_RATIO

dbClient = DbClient()
user_info_context = UserInfoContext()


class DialogSignals(QtCore.QObject):
    CLOSE = QtCore.pyqtSignal()


class FriendFindDialog(QWidget):

    def __init__(self, parent=None):
        super(FriendFindDialog, self).__init__(parent)
        self.SIGNALS = DialogSignals()
        self.initUI()

    def initUI(self):
        self.setFixedWidth(400 * SCREEN_RATIO[0])
        self.resize(400 * SCREEN_RATIO[0], 500 * SCREEN_RATIO[1])
        self.setWindowTitle('친구추가')
        self.setWindowIcon(QtGui.QIcon(UIConst.DOTALK_ICON))

        _layout = QVBoxLayout()
        _layout.setAlignment(QtCore.Qt.AlignTop)

        title = QHBoxLayout()
        title.setAlignment(QtCore.Qt.AlignCenter)
        title_label = QLabel('친구추가')
        title_label.setFont(QFont('맑은 고딕', 20))
        title.addWidget(title_label)

        searchbar = QHBoxLayout()
        self.searchedit = QLineEdit()
        self.searchedit.returnPressed.connect(self._onSearchClicked)
        self.searchedit.setPlaceholderText('이름을 입력해주세요')
        self.searchbtn = QPushButton('검색')
        self.searchbtn.clicked.connect(self._onSearchClicked)
        searchbar.addWidget(self.searchedit)
        searchbar.addWidget(self.searchbtn)

        FriendFindPage.addFriendCbk = self._onAddClicked
        self.friendList = FriendFindPage()

        _layout.addWidget(title)
        _layout.addLayout(searchbar)
        _layout.addWidget(self.friendList)

        self.setLayout(_layout)

    def _onSearchClicked(self):
        q = self.searchedit.text()
        if q == '':
            QMessageBox.about(self, '두톡', '이름을 입력해주시기 바랍니다.')
            return
        except_list = [info.h_userid for info in user_info_context.getFriendsInfo()] + [user_info_context.getMyInfo().h_userid]
        findlist = [info for info in dbClient.searchUserByName(q) if info.h_userid not in except_list]
        self.friendList.updateList(findlist)

    def _onAddClicked(self, hid):
        result = user_info_context.addFriendByHashedUserid(hid)
        if result:
            QMessageBox.about(self, '친구 추가', '성공')
        else:
            QMessageBox.about(self, '친구 추가', '실패')

    def closeEvent(self, e):
        self.SIGNALS.CLOSE.emit()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dialog = FriendFindDialog()
    dialog.show()
    sys.exit(app.exec_())
