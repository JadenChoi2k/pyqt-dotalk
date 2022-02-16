import sys, time, threading, math
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from model.chat_dto import ChatDto
from model.chat_room import ChatRoom
from model.user_info_dto import UserInfoDto
from model.user import User
from pages.chatting.sidebar import Sidebar
from ui.ui_const import UIConst
from icons import svgtxt
from ui.component.home.menu_item_by_svgtxt import MenuItemBySvgText
from preferences import SCREEN_RATIO

'''
-----------------
|    navbar     |
-----------------
|   chat box    |
-----------------
|   chat edit   |
-----------------
'''


class ChattingRoomSignals(QObject):
    SEND = pyqtSignal(ChatDto)
    CLOSE = pyqtSignal(str)


class ChattingRoom(QWidget):

    _user: User = None
    '''
    ui contents
    '''
    # navbar
    _navbar: QHBoxLayout = None
    _navbar_wrap: QGroupBox = None
    # chat box
    _scroll_box: QScrollArea = None
    _wrap: QGroupBox = None
    _chat_box: QVBoxLayout = None
    # chat edit
    _chatting_section: QHBoxLayout = None
    _chat_edit: QTextEdit = None
    _send_btn: QPushButton = None
    # sidebar
    _sidebar: Sidebar = None
    _sidebar_flag: bool = None
    _sidebar_pushing: bool = None
    # signals
    remv_t: QThread = None
    SIGNALS: ChattingRoomSignals = None

    def __init__(self, user:User, chatroom:ChatRoom):
        super().__init__()
        self._user = user
        self._chatroom = chatroom
        self.SIGNALS = ChattingRoomSignals()
        self.initUI()

    def createRemoveThread(self):
        self.remv_t = RemoveLineShiftThread()
        self.remv_t.removeChat.connect(self.removeChat)
        self.remv_t.start()

    def initUI(self):
        self.__navbar()
        self.__chatShowbox()
        self.__chatEditbox()
        self.__setWholeLayout()
        self.__setWindow()
        self.__initChat()

    def __navbar(self):
        self._navbar = QHBoxLayout()
        self._navbar.setContentsMargins(0, 0, 0, 0)
        _navbar_wrap = QWidget()
        _navbar_wrap.setStyleSheet(f'border:none; background:{UIConst.SKYBLUE};')
        _navbar_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        _navbar_wrap.setLayout(self._navbar)
        self._navbar_wrap = _navbar_wrap

        self.nav_label = QLabel(self._chatroom.getName(my_hid=self._user.get_hashed_userid()))
        self.nav_label.setFont(QFont('맑은 고딕', 15))
        nav_item = MenuItemBySvgText(svgtxt.getListMenuText(), width=25, height=25)
        nav_item.clicked.connect(self._showSidebar)

        self._navbar.addSpacing(10)
        self.addNavitem(self.nav_label)
        self._navbar.addStretch(1)
        self.addNavitem(nav_item)

    def __chatShowbox(self):
        self._chat_show_box = QVBoxLayout()
        self._chat_show_box.setSpacing(0)
        self._scroll_box = QScrollArea()
        self._scroll_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._scroll_box.verticalScrollBar().setStyleSheet('QScrollBar {width:8px}\nQScrollBar:hover {width:20px}')
        self._scroll_box.setWidgetResizable(True)
        self._scroll_box.setStyleSheet(f'border:none; background:{UIConst.SKYBLUE}')
        self._chat_box = QVBoxLayout()
        self._chat_box.setAlignment(Qt.AlignTop)
        self._chat_box.setContentsMargins(0, 0, 0, 0)
        self._wrap = QWidget()
        self._wrap.setStyleSheet('border:none;')
        self._wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._wrap.setLayout(self._chat_box)
        self._scroll_box.setWidget(self._wrap)

        self._chat_show_box.addWidget(self._navbar_wrap, 1)
        self._chat_show_box.addWidget(self._scroll_box, 12)

    def __chatEditbox(self):
        self._chat_edit = QTextEdit()
        self._chat_edit.installEventFilter(self)
        self._send_btn = QPushButton(' 전송 ')
        self._send_btn.setStyleSheet('border:1px solid #aaaaaa; border-radius:3px;')
        self._send_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self._send_btn.clicked.connect(self.sendMsg)
        self._chatting_section = QHBoxLayout()
        self._chatting_section.addWidget(self._chat_edit)
        self._chatting_section.addWidget(self._send_btn)

    def __setWholeLayout(self):
        ui_layout = QVBoxLayout()
        ui_layout.setSpacing(0)
        ui_layout.setContentsMargins(0, 0, 0, 0)
        ui_layout.addLayout(self._chat_show_box, 16)
        ui_layout.addLayout(self._chatting_section, 2)
        self.setLayout(ui_layout)

    def __setWindow(self):
        self.resize(350 * SCREEN_RATIO[0], 650 * SCREEN_RATIO[1])
        self.setWindowTitle('두톡')
        self.setWindowIcon(QIcon(UIConst.DOTALK_ICON))

    def __initChat(self):
        chats: list = self._chatroom.getWholeChat()
        for idx, chat in enumerate(chats):
            if idx == 0:
                idx = 1
            self.addChatboxByChatDto(chat, chats[idx - 1])

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Shift:
            self._shift_pushing = True
        if event.type() == QEvent.KeyRelease and event.key() == Qt.Key_Shift:
            self._shift_pushing = False
        if event.type() == QEvent.KeyPress and obj is self._chat_edit:
            if self._chat_edit.hasFocus() and event.key() == Qt.Key_Return:
                if self._shift_pushing:
                    pass
                else:
                    if self._chat_edit.toPlainText().strip():
                        self.sendMsg()
        return super().eventFilter(obj, event)

    def addNavitem(self, item:QWidget):
        self._navbar.addWidget(item)

    def _showSidebar(self):
        self._sidebar = Sidebar(self)
        self._sidebar.setChatters(list(self._chatroom.getUsers().values()))
        self._sidebar.updateUI()
        self._sidebar_flag = True
        self._sidebar.move(0, 0)
        self._sidebar.resize(self.width(), self.height())
        self._sidebar.SIGNALS.CLOSE.connect(self._hideSidebar)
        self._sidebar.show()

    def _hideSidebar(self):
        self._sidebar.close()
        self._sidebar_flag = False

    def addChatboxByChatDto(self, chat:ChatDto, lastchat:ChatDto=None):
        if lastchat is None:
            lastchat = self._chatroom.getLastChatsByNumber(2)
            if len(lastchat) > 1:
                lastchat = lastchat[0]
        if isinstance(lastchat, ChatDto) and chat.time.date() != lastchat.time.date():
            self.addDayChangeIndicator(chat.time.date())
        if chat.h_userid == self._user.get_hashed_userid():
            self.addChatbox(self.myMsgbox(chat))
        else:
            self.receiveChat(chat)

    def addChatbox(self, msg_box:QVBoxLayout):
        self._chat_box.addLayout(msg_box)
        threading.Thread(target=self.setScrollBot, args=()).start()

    def addIndicator(self, txt:str):
        indicator = QHBoxLayout()
        indicator.setAlignment(Qt.AlignHCenter)
        indicator.addWidget(getIndicatorBrowser(txt, 'rgba(20, 20, 20, 0.4)', 'rgba(240, 240, 240, 0.9)'))
        self._chat_box.addLayout(indicator)

    def addDayChangeIndicator(self, _date:datetime):
        date_txt = f'{_date.year}년 {_date.month}월 {_date.day}일'
        indicator = QHBoxLayout()
        indicator.addStretch(1)
        indicator.addWidget(getDayChangeIndicator(date_txt), 8)
        indicator.addStretch(1)
        self._chat_box.addLayout(indicator)

    def setScrollBox(self):
        time.sleep(0.01)
        self._scroll_box.verticalScrollBar().setValue(self._scroll_box.verticalScrollBar().maximum())

    def receiveChat(self, chatdto:ChatDto):
        userinfo = self._chatroom.getUserByHashedUserid(chatdto.h_userid)
        self.addChatbox(msgbox(chatdto, userinfo))

    def removeChat(self):
        self._chat_edit.clear()

    def sendMsg(self):
        msg = self._chat_edit.toPlainText()

        chatdto = ChatDto()
        chatdto.chatRoomId = self._chatroom.getRoomid()
        chatdto.h_userid = self._user.get_hashed_userid()
        chatdto.msg = msg
        chatdto.time = datetime.now()
        self.SIGNALS.SEND.emit(chatdto)
        self.addChatboxByChatDto(chatdto)
        self.createRemoveThread()

    def myMsgbox(self, chatdto:ChatDto)->QLayout:
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignRight)
        myname_hbox = QHBoxLayout()
        myname_hbox.setAlignment(Qt.AlignRight)
        myname_hbox.addSpacing(7)
        vbox.addLayout(myname_hbox)
        msg_hbox = QHBoxLayout()
        msg_hbox.setAlignment(Qt.AlignRight)
        msg_time = QLabel(chatdto.time.strftime('%H:%M'))
        msg_time.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        msg_time_vbox = QVBoxLayout()
        msg_time_vbox.setAlignment(Qt.AlignBottom)
        msg_time_vbox.addWidget(msg_time)
        msg_time_vbox.addSpacing(2)
        msg_txt = getMsgtxtBrowser(chatdto.msg, UIConst.YELLOW)
        msg_hbox.addLayout(msg_time_vbox)
        msg_hbox.addWidget(msg_txt)
        msg_hbox.addSpacing(5)
        vbox.addLayout(msg_hbox)
        return vbox

    def resizeEvent(self, event):
        if self._sidebar_flag:
            self._sidebar.move(0, 0)
            self._sidebar.resize(self.width(), self.height())

    def closeEvent(self, event):
        self.SIGNALS.CLOSE.emit(self._chatroom.getRoomid())


# emit signal after waiting 0.02 seconds
class RemoveLineShiftThread(QThread):
    removeChat = pyqtSignal()

    def run(self):
        time.sleep(0.02)
        self.removeChat.emit()


def msgbox(chatdto:ChatDto, info:UserInfoDto)->QLayout:
    vbox = QVboxLayout()
    vbox.setAlignment(Qt.AlignLeft)
    name_lbl = QLabel()
    if isinstance(info, UserInfoDto):
        name_lbl.setText(info.name)
    name_hbox = QHBoxLayout()
    name_hbox.setAlignment(Qt.AlignLeft)
    name_hbox.addSPacing(7)
    name_hbox.addWidget(name_lbl)
    vbox.addLayout(name_hbox)

    msg_hbox = QHBoxLayout()
    msg_hbox.setAlignment(Qt.AlignLeft)
    msg_time = QLabel(chatdto.time.strftime('%H:%M'))
    msg_time.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    msg_time_vbox = QVBoxLayout()
    msg_time_vbox.setAlignment(Qt.AlignBottom)
    msg_time_vbox.addWidget(msg_time)
    msg_txt = getMsgtxtBrowser(chatdto.msg, UIConst.WHITE)
    msg_hbox.addSpacing(5)
    msg_hbox.addWidget(msg_txt)
    msg_hbox.addWidget(msg_time_vbox)
    vbox.addLayout(msg_hbox)
    return vbox


def getMsgtxtBrowser(txt:str, bg_color:str=UIConst.WHITE, txt_color:str='black')->QTextBrowser:
    msg_txt = QTextBrowser()
    msg_txt.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
    msg_txt.setAlignment(Qt.AlignCenter)
    msg_txt.setFont(QFont(UIConst.DEFAULT_FONT, 12))
    msg_txt.setPlainText(txt)
    msg_txt.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    font = msg_txt.document().defaultFont()
    font_metrics = QFontMetrics(font)
    # calculate size of message box
    w_max = 270
    w = 0
    h = 20
    for line in txt.split('\n'):
        text_size = font_metrics.size(0, line)
        lw = text_size.width() + 30
        lh = text_size.height()
        if lw >= w_max:
            line_num = math.floor(lw / w_max)
            lh = lh + text_size.height() * line_num
        w = max(w, lw)
        h += lh
    w = min(w, w_max)
    msg_txt.setFixedSize(w, h)
    msg_txt.setStyleSheet(f'background:{bg_color}; border-radius:15px; padding:5px 10px; color:{txt_color};')
    return msg_txt


def getIndicatorBrowser(txt:str, bg_color:str=UIConst.NAVY, txt_color:str='white')->QTextBrowser:
    msg_txt = QTextBrowser()
    msg_txt.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
    msg_txt.setAlignment(Qt.AlignCenter)
    msg_txt.setFont(QFont(UIConst.DEFAULT_FONT, 8))
    msg_txt.setPlainText(txt)
    msg_txt.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    font = msg_txt.document().defaultFont()
    font_metrics = QFontMetrics(font)

    text_size = font_metrics.size(0, txt)
    w = text_size.width() + 30
    h = text_size.height() + 20
    msg_txt.setFixedSize(w, h)
    msg_txt.setStyleSheet(f'background:{bg_color}; border-radius:15px; padding:5px 10px; color:{txt_color};')
    return msg_txt


def getDayChangeIndicator(txt:str, color:str='#2f2f2f')->QWidget:
    widget = QWidget()
    widget.setMinimumWidth(200)
    widget.setMaximumWidth(400)
    _layout = QHBoxLayout()
    left_line = QWidget()
    left_line.setFixedHeight(1)
    left_line.setStyleSheet(f'background: {color};')
    date_label = QLabel(txt)
    date_label.setFont(QFont('맑은 고딕', 10))
    date_label.setAlignment(Qt.AlignCenter)
    date_label.setStyleSheet(f'color: {color}')
    right_line = QWidget()
    right_line.setFixedHeight(1)
    right_line.setStyleSheet(f'background: {color};')
    _layout.addWidget(left_line)
    _layout.addSpacing(20)
    _layout.addWidget(date_label)
    _layout.addSpacing(20)
    _layout.addWidget(right_line)
    widget.setLayout(_layout)
    return widget


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.exit(app.exec_())
