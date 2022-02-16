import threading
from PyQt5 import QtCore
from model.chat_dto import ChatDto
from model.user_info_dto import UserInfoDto
from network.chat.client.chatting_client import ChattingClient


class ChattingSignals(QtCore.QObject):
    RECEIVED = QtCore.pyqtSignal(ChatDto)


class ChattingClientService:
    _client:ChattingClient = None
    SIGNALS:ChattingSignals = ChattingSignals()
    recv_t = None

    def __init__(self, session_id:str = None):
        self._client = ChattingClient()
        if session_id:
            self.connect_server(session_id)

    def connect_server(self, sessionkey):
        self._client.connectToServer()
        self._client.sendMessage(sessionkey)
        self.run_receive_loop()

    def run_receive_loop(self):
        if self.recv_t is None:
            self.recv_t = threading.Thread(target=self.recv_loop, args=())
            self.recv_t.start()

    def sendChat(self, chatdto:ChatDto):
        self._client.sendChat(chatdto)

    def recv_loop(self):
        while True:
            if not self._client:
                return
            chat:ChatDto = self._client.receiveChat()
            if chat:
                self.SIGNALS.RECEIVED.emit(chat)

    def disconnect(self):
        self._client.disconnect()
        self.recv_t = None
        self._client = None
