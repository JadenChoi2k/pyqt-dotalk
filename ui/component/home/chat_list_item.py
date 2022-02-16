from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from util import utils
from ui.ui_const import UIConst
from model.chat_dto import ChatDto
import json


class ChatListItem(QWidget):
    clicked_cbk = QtCore.pyqtSignal(str)
    roomid = None
    chat_name = None
    last_chat: ChatDto = None
    color = UIConst.BLUE
    read_num: int = None

    def __init__(self, roomid=None, chat_name='채팅방', last_chat=None, color=UIConst.BLUE, read_num=0):
        super().__init__()
        self.roomid = roomid
        self.chat_name = chat_name
        self.last_chat = last_chat
        self.color = color
        self.read_num = read_num

        self.initUI()
        utils.clickable(self).connect(self._whenClicked)

    def initUI(self):
        self.setFixedHeight(55)
        self._chat_color = QWidget()
        self._chat_color.setFixedSize(40, 40)
        self.setColor(self.color)
        self._name_label = QLabel(self.chat_name)
        self._read_num_label = QLabel()
        self._read_num_label.setFixedHeight(18)
        self._read_num_label.setMinimumWidth(18)
        self._read_num_label.setStyleSheet(f'padding-left:3px; border-radius:9px; background-color:{UIConst.ORANGE}; color:white')
        self.setReadNum(self.read_num)
        self._time = QLabel()
        self._lastmsg = QLabel()
        self._lastmsg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._lastmsg.setFixedHeight(25)
        self._lastmsg.setWordWrap(True)
        self.setLastChat(self.last_chat)

        ui_layout = QHBoxLayout()
        ui_layout.setContentsMargins(0, 0, 0, 0)
        ui_layout.addWidget(self._chat_color)

        right_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        top_layout.addWidget(self._name_label)
        top_layout.addSpacing(5)
        top_layout.addWidget(self._read_num_label)
        top_layout.addStretch(1)
        top_layout.addWidget(self._time)

        bottom_layout = QHBoxLayout()

        bottom_left_layout = QVBoxLayout()
        bottom_left_layout.setAlignment(QtCore.Qt.AlignTop)
        bottom_left_layout.addWidget(self._lastmsg)
        bottom_right_layout = QVBoxLayout()
        bottom_right_layout.setContentsMargins(0, 0, 0, 0)
        bottom_right_layout.setSpacing(0)
        bottom_right_layout.setAlignment(QtCore.Qt.AlignCenter)

        bottom_layout.addLayout(bottom_left_layout)
        bottom_layout.addStretch(1)
        bottom_layout.addLayout(bottom_right_layout)

        right_layout.addLayout(top_layout)
        right_layout.addLayout(bottom_layout)

        ui_layout.addLayout(right_layout)
        self.setLayout(ui_layout)

    def getRoomid(self):
        return self.roomid

    def setRoomid(self, ri):
        self.roomid = ri

    def setColor(self, color):
        self._chat_color.setStyleSheet(f'border-radius:20px; background-color:{color};')

    def setLastChat(self, chatDto:ChatDto):
        if not isinstance(chatDto, ChatDto):
            return None

        self.last_chat = chatDto
        if isinstance(self._lastmsg, QLabel):
            self._lastmsg.setText(chatDto.msg)
        if isinstance(self._time, QLabel):
            self._time.setText(chatDto.time.strftime("%p %I:%M"))

    def setChatName(self, name):
        self.chat_name = name
        self._name_label.setText(name)

    def setReadNum(self, num:int):
        self.read_num = num
        self._read_num_label.setText(str(num))
        if num > 0:
            self._read_num_label.show()
        else:
            self._read_num_label.hide()

    def _whenClicked(self):
        self.clicked_cbk.emit(self.roomid)

    def toJson(self):
        dic = {}

        dic['roomid'] = self.roomid
        dic['chat_name'] = self.chat_name
        dic['last_chat'] = self.last_chat.toJson()
        dic['color'] = self.color
        dic['read_num'] = self.read_num

        return json.dumps(dic)

    @staticmethod
    def fromJson(data):
        dic = json.loads(data)
        return ChatListItem(
            roomid=dic.get('roomid'),
            chat_name=dic.get('chat_name'),
            last_chat=ChatDto.fromJson(dic.get('last_chat')),
            color=dic.get('color'),
            read_num=dic.get('read_num')
        )
