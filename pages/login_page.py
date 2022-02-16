import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ui.ui_const import UIConst
from model.user_login_form import UserLoginForm
from pages.join_page import JoinPage
from network.database.client.db_client import DbClient
from preferences import SCREEN_RATIO
import preferences

dbClient = DbClient()


class LoginPage(QWidget):

    joinPage = None

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.logo_lbl = self.createLogoLabel()
        self.form_layout = self.createFormLayout()
        self.layout = self.createWholeLayout()

        self.setLayout(self.layout)
        self.ratio_setFixedSize(350, 600)
        self.setWindowTitle('로그인')
        self.setWindowIcon(QIcon(UIConst.DOTALK_ICON))
        self.show()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return:
            self.loginButtonClicked()

    def createLogoLabel(self):
        logo = QPixmap()
        logo.load(UIConst.DOTALK_ICON)
        logo_lbl = QLabel()
        logo_lbl.setPixmap(logo)
        logo_lbl.setCursor(QCursor(Qt.PointingHandCursor))
        logo_lbl.setToolTip('처음이신가요? 회원가입')
        clickable(logo_lbl).connect(self.logoClicked)
        return logo_lbl

    def createFormLayout(self):
        id_hbox = QHBoxLayout()
        self.id_edit = QLineEdit()
        self.id_edit.setValidator(QRegExpValidator(QRegExp('[A-z0-9]{0,15}')))
        self.id_edit.ratio_setFixedSize(250, 30)
        self.id_edit.setStyleSheet('border-radius:25%; padding-left:10px; font-size:15px')
        self.id_edit.setPlaceholderText('아이디를 입력하세요')
        id_hbox.addWidget(self.id_edit)

        pw_hbox = QHBoxLayout()
        self.pw_edit = QLineEdit()
        self.pw_edit.ratio_setFixedSize(250, 30)
        self.pw_edit.setStyleSheet('border-radius:25%; padding-left:10px; font-size:15px;')
        self.pw_edit.setPlaceholderText('비밀번호를 입력하세요')
        self.pw_edit.setEchoMode(QLineEdit.Password)
        pw_hbox.addWidget(self.pw_edit)

        btn_hbox = QHBoxLayout()
        btn_hbox.setAlignment(Qt.AlignCenter)
        self.login_btn = QPushButton('로그인')
        self.login_btn.ratio_setFixedSize(100, 40)
        self.login_btn.setStyleSheet(f'color:white; background-color:{UIConst.BLUE}; border-radius:33%;')
        self.login_btn.clicked.connect(self.loginButtonClicked)
        btn_hbox.addWidget(self.login_btn)

        vbox = QVBoxLayout()
        vbox.addLayout(id_hbox)
        vbox.addLayout(pw_hbox)
        vbox.addSpacing(15)
        vbox.addLayout(btn_hbox)

        return vbox

    def createWholeLayout(self):
        layout = QVBoxLayout()
        logo_hbox = QHBoxLayout()
        logo_hbox.setAlignment(Qt.AlignHCenter)
        logo_hbox.addWidget(self.logo_lbl)
        layout.addStretch(1)
        layout.addLayout(logo_hbox, 5)
        layout.addLayout(self.form_layout, 2)
        layout.addStretch(2)
        return layout

    def loginButtonClicked(self):
        userid = self.id_edit.text()
        password = self.pw_edit.text()
        form = UserLoginForm(userid, password)
        login = dbClient.login(form)
        if isinstance(login, tuple):
            if login[0]:
                QMessageBox.about(self, '두톡', f'{login[1]}님 환영합니다.')
                self.close()
            else:
                QMessageBox.about(self, '두톡', '로그인에 실패하였습니다.')

    def logoClicked(self):
        self.joinPage = JoinPage()
        self.joinPage.show()

    def closeAll(self):
        if self.joinPage:
            self.joinPage.close()

    def closeEvent(self, event):
        self.closeAll()


def clickable(widget):

    class Filter(QObject):

        clicked = pyqtSignal()

        def eventFilter(self, obj, event):
            if obj == widget:
                if event.type() == QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit()
                        return True
            return False

    _filter = Filter(widget)
    widget.installEventFilter(_filter)
    return _filter.clicked


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LoginPage()
    sys.exit(app.exec_())
