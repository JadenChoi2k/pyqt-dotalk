from socket import *
from model.chat_dto import ChatDto
from network import settings

IP = settings.CHAT_IP
PORT = settings.CHAT_PORT


class ChattingClient:
    # singleton
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    _hid = None
    _socket = None

    def __init__(self, h_userid:str=None):
        if h_userid:
            self._hid = h_userid

    def connectToServer(self, ip:str = IP, port:int = PORT):
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.connect((ip, port))
        print('connected to chatting server')

    def isconnected(self):
        return self._socket and not self._socket._closed

    def sendMessage(self, msg:str):
        self._socket.send(msg.encode('utf-8'))

    def sendChat(self, chatdto:ChatDto):
        self._socket.send(chatdto.toJson().encode('utf-8'))

    def receiveChat(self):
        try:
            recvData = self._socket.recv(1024).decode('utf-8')
            chat = ChatDto.fromJson(recvData)
            return chat
        except ConnectionAbortedError or OSError:
            print('chatting client disconnected')

    def disconnect(self):
        self.sendMessage('close')
        self._socket.close()
        print('disconnect from chatting server')

