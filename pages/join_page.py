import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QRegExp, QDate
from ui.ui_const import UIConst
from model.user_join_form import UserJoinForm
from model.validator.user_validator import UserValidator
from network.database.client.db_client import DbClient

dbClient = DbClient()


class JoinPage(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowSettings()

    def initUI(self):
        main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignCenter)
        top_logo = QLabel()
        logo_pixmap = QPixmap()
        logo_pixmap.load(UIConst.DOTALK_ICON)
        top_logo.setPixmap(logo_pixmap)
        top_label = QLabel('회원가입')
        top_label.setAlignment(Qt.AlignCenter)
        top_font = top_label.font()
        top_font.setFamily('맑은 고딕')
        top_font.setPointSize(20)
        top_label.setFont(top_font)
        top_layout.addWidget(top_logo)
        top_layout.addWidget(top_label)

        form_layout = QFormLayout()
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(10, 0, 10, 0)

        id_layout = self.createIdLayout()
        form_layout.addRow('아이디', id_layout)
        self.pw_edit = self.createPasswordEdit()
        form_layout.addRow('비밀번호', self.pw_edit)
        self.pw_edit_confirm = self.createPasswordEdit()
        form_layout.addRow('비밀번호 확인', self.pw_edit_confirm)
        self.name_edit = lineEdit(placeholder='이름을 입력하세요', validator=QRegExpValidator(QRegExp('[가-힣]{2,8}|[A-z]{2,16}')))
        form_layout.addRow('이름', self.name_edit)
        self.department_edit = lineEdit(placeholder='부서를 입력하세요', validator=QRegExpValidator(QRegExp('[가-힣0-9 ]{2, 15}')))
        form_layout.addRow('부서', self.department_edit)
        self.position_edit = lineEdit(placeholder='직급을 입력하세요', validator=QRegExpValidator(QRegExp('[가-힣 ]{2, 12}')))
        form_layout.addRow('직급', self.position_edit)
        self.birth_form = self.createBirthDateEdit()
        form_layout.addRow('생일', self.birth_form)

        bottom_layout = QHBoxLayout()
        bottom_layout.setAlignment(Qt.AlignCenter)
        self.join_btn = QPushButton('회원가입')
        self.join_btn.ratio_setFixedSize(100, 40)
        self.join_btn.setStyleSheet(f'color:white; background-color:{UIConst.ORANGE}; border-radius:33%;')
        self.join_btn.clicked.connect(self._joinClicked)
        bottom_layout.addWidget(self.join_btn)

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)
        self.setWindowTitle('회원가입')

    def setWindowSettings(self):
        self.ratio_setFixedSize(350, 550)
        self.setWindowIcon(QIcon(UIConst.DOTALK_ICON))

    def createIdLayout(self):
        id_layout = QHBoxLayout()
        self.id_edit = self.createIdEdit()
        self.id_confirmbtn = QPushButton('중복 확인')
        self.id_confirmbtn.ratio_setFixedSize(65, 25)
        self.id_confirmbtn.setStyleSheet(f'color:white; background-color:{UIConst.BLUE}; border-radius:12px;')
        self.id_confirmbtn.clicked.connect(self._idConfirmClicked)
        id_layout.addWidget(self.id_edit)
        id_layout.addWidget(self.id_confirmbtn)
        return id_layout

    def createIdEdit(self):
        return lineEdit(placeholder='아이디를 입력하세요', validator=QRegExpValidator(QRegExp('[A-z0-9]{0, 15}')))

    def createPasswordEdit(self):
        return lineEdit(placeholder='비밀번호를 입력하세요',
                        validator=QRegExpValidator(QRegExp(r"[A-z0-9`~!@#$%^&*-_=+;:'\",<.>/?]{0, 20}")),
                        echoMode=QLineEdit.Password)

    def createBirthDateEdit(self):
        curDate = QDate.currentDate()
        minBirthDate = curDate.addYears(-100)
        defaultBirthDate = curDate.addYears(-20)
        maxBirthDate = curDate.addYears(-15)
        birth_form = QDateEdit()
        birth_form.setDisplayFormat('yyyy-MM-dd')
        birth_form.setCalendarPopup(True)
        birth_form.setDate(defaultBirthDate)
        birth_form.setMinimumDate(minBirthDate)
        birth_form.setMaximumDate(maxBirthDate)
        return birth_form

    def _idConfirmClicked(self):
        userid = self.id_edit.text()
        if not UserValidator().validUserid(userid):
            QMessageBox.about(self, "아이디 형식이 잘못되었습니다.", '아이디는 영문, 숫자로 구성된 4~15자입니다.')
            return
        isoverlapped = dbClient.isoverlap(userid)
        if isoverlapped:
            QMessageBox.about(self, '중복 확인', '중복되었습니다.')
        else:
            QMessageBox.about(self, '중복 확인', '사용 가능합니다.')

    def _joinClicked(self):
        userid = self.id_edit.text()
        password = self.pw_edit.text()
        password_confirm = self.pw_edit_confirm.text()
        if password != password_confirm:
            QMessageBox.about(self, '비밀번호 확인', '비밀번호를 다시 입력해주세요')
            self.pw_edit_confirm.clear()
            return
        name = self.name_edit.text()
        department = self.department_edit.text()
        position = self.position_edit.text()
        birthday = self.birth_form.date().toPyDate()
        form = UserJoinForm(
            userid,
            password,
            name,
            department,
            position,
            birthday,
            UIConst.SKYBLUE
        )
        joined = dbClient.join(form)
        if isinstance(joined, tuple):
            if joined[0]:
                QMessageBox.about(self, '회원가입', '가입을 축하합니다!')
                self.close()
            else:
                QMessageBox.about(self, '회원가입', f'가입에 실패하였습니다\n사유 : {joined[1]}')


def lineEdit(borderradius=10, paddingLeft=10, fontsize=15, width=None, height=25, placeholder=None, validator=None, echoMode=None):
    _lineEdit = QLineEdit()
    _lineEdit.setStyleSheet(f'border-radius:{borderradius}; padding-left:{paddingLeft}; font-size:{fontsize};')

    if width:
        _lineEdit.ratio_setFixedWidth(width)
    if height:
        _lineEdit.ratio_setFixedHeight(height)
    if placeholder:
        _lineEdit.setPlaceholderText(placeholder)
    if validator:
        _lineEdit.setValidator(validator)
    if echoMode:
        _lineEdit.setEchoMode(echoMode)

    return _lineEdit


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = JoinPage()
    ex.show()
    sys.exit(app.exec_())
