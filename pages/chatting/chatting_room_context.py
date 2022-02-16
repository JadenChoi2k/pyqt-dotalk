from PyQt5 import QtCore
from collections import deque
from model.chat_dto import ChatDto
from model.chat_room import ChatRoom
from pages.chatting.chatting_room import ChattingRoom
from network.database.client.db_client import DbClient
from network.chat.client.chatting_client_service import ChattingClientService
from util import utils
import os

dbClient = DbClient()
LOG_PATH = f'.\pages\chatting\chatlog'


def get_user_path():
    try:
        return os.path.join(LOG_PATH, utils.filter_window_path(dbClient.getUser().get_hashed_userid()))
    except Exception as e:
        print(e, '\ndb client has not user')


class ChattingRoomContextSignals(QtCore.QObject):
    SEND = QtCore.pyqtSignal(ChatDto)
    RECEIVED = QtCore.pyqtSignal(ChatDto)
    READ = QtCore.pyqtSignal(str)
    UPDATE_ROOM = QtCore.pyqtSignal(str, str)


class ChattingRoomContext:
    # singleton
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    rooms = {} # roomid : chat room
    current_widgets = {} # roomid : chatting room
    SIGNALS = ChattingRoomContextSignals()
    chatserv = None

    def connect_server(self):
        sessionId = dbClient.getSessionId()
        if sessionId:
            self.chatserv = ChattingClientService(sessionId)
            self.chatserv.SIGNALS.RECEIVED.connect(self.receiveChat)
        else:
            print('fail to connect server : has no session key')

    def receiveChat(self, chatdto:ChatDto):
        roomid = chatdto.chatRoomId
        chatting_widget = self.current_widgets.get(roomid)
        self.SIGNALS.RECEIVED.emit(chatdto)
        if chatting_widget:
            room = self.rooms.get(roomid)
            if isinstance(room, ChatRoom):
                room.addChat(chatdto)
                chatting_widget.addChatboxByChatDto(chatdto)
                self.SIGNALS.READ.emit(roomid)
            else:
                chatroom:ChatRoom = self.rooms.get(roomid)
                if chatroom:
                    chatroom.addChat(chatdto)
                else:
                    chatroom = dbClient.getChatRoomById(roomid)
                    self.SIGNALS.UPDATE_ROOM.emit(roomid, chatroom.getName())
                    chatroom.addChat(chatdto)
                    self.rooms[roomid] = chatroom

    def isexist(self, roomid):
        if self.rooms.get(roomid):
            return True
        else:
            return False

    def addChattingRoom(self, chatroom:ChatRoom):
        roomid = chatroom.getRoomid()
        self.SIGNALS.READ.emit(roomid)
        exist_widget = self.current_widgets.get(roomid)
        # TODO : if widget exists, then focus on it
        if exist_widget:
            return
        exist_room = self.rooms.get(chatroom.getRoomid())
        if exist_room:
            chatroom = exist_room

        chat_room_widget = ChattingRoom(dbClient.getUser(), chatroom)
        chat_room_widget.SIGNALS.SEND.connect(self._whenSend)
        chat_room_widget.SIGNALS.CLOSE.connect(self._whenClosed)
        self.current_widgets[roomid] = chat_room_widget
        self.rooms[roomid] = chatroom
        self.current_widgets[roomid].show()

    def getNextWindowPosition(self):
        num = len(self.current_widgets)
        return num * 60, num * 25

    def openChattingRoom(self, roomid):
        chatroom:ChatRoom = self.rooms.get(roomid)
        chatroom_from_server = dbClient.getChatRoomById(roomid)
        chatroom.setUsers(chatroom_from_server.getUsers())

        if not chatroom:
            print('non-existent chatting room', roomid)
            return None

        chat_room_widget = ChattingRoom(dbClient.getUser(), chatroom)
        chat_room_widget.SIGNALS.SEND.connect(self._whenSend)
        chat_room_widget.SIGNALS.CLOSE.connect(self._whenClosed)
        self.SIGNALS.READ.emit(roomid)
        self.current_widgets[roomid] = chat_room_widget
        self.current_widgets[roomid].show()

    def _whenSend(self, chat:ChatDto):
        if hasattr(self, 'chatserv'):
            self.chatserv.sendChat(chat)
        room:ChatRoom = self.rooms.get(chat.chatRoomId)
        if room:
            room.addChat(chat)
        self.SIGNALS.SEND.emit(chat)
        self.SIGNALS.READ.emit(chat.chatRoomId)

    def _whenClosed(self, roomid):
        try:
            self.current_widgets.pop(roomid)
            self._writeChattingLog()
        except KeyError as e:
            print(e, 'already closed window')
        except Exception as e:
            print('unexpected error', e)

    def getChatRoomNameById(self, roomid):
        chatroom = self.rooms.get(roomid)
        if isinstance(chatroom, ChatRoom):
            return chatroom.getName()

    def updateChatRoomNames(self):
        for room in self.rooms.values():
            if isinstance(room, ChatRoom):
                self.SIGNALS.UPDATE_ROOM.emit(room.getRoomid(),
                                              room.getName(dbClient.getUserHashedIdBySessionKey(dbClient.getSessionId())))

    def _whenChangedRoomName(self, roomid, name):
        room = self.rooms.get(roomid)
        if isinstance(room, ChatRoom):
            room.setName(name)
        self.SIGNALS.UPDATE_ROOM.emit(roomid, name)

    def closeConnection(self):
        self.chatserv.disconnect()

    def _writeChattingLog(self):
        for room in self.rooms.values():
            if not isinstance(room, ChatRoom):
                continue
            room:ChatRoom = room

            user_path = get_user_path()
            if not os.path.isdir(user_path):
                os.mkdir(user_path)

            dest_path = os.path.join(user_path, room.getRoomid())
            if not os.path.isdir(dest_path):
                os.mkdir(dest_path)

            with open(os.path.join(dest_path, 'chat.log'), 'wt') as f:
                f.writelines([chat.toJson() for chat in room.getWholeChat()])

    @staticmethod
    def fromChattingLog():
        chat_context = ChattingRoomContext()
        user_path = get_user_path()
        if not os.path.isdir(user_path):
            return chat_context
        for roomid in os.listdir(user_path):
            chatroom = ChatRoom()
            chatroom = dbClient.getChatRoomById(roomid)
            src = os.path.join(user_path, roomid, 'chat.log')
            if not os.path.isfile(src):
                continue
            with open(src, 'rt') as f:
                for idx, line in enumerate(f.readlines()):
                    try:
                        chat = ChatDto.fromJson(line.strip())
                        chatroom.addChat(chat)
                    except:
                        continue
            chat_context.rooms.update([(roomid, chatroom)])
        print('load from chatting logs')
        return chat_context

    # TODO : make this
    def getRoomsFromServer(self):
        pass
