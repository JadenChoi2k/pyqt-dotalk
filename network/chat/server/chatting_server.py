import sys, os, datetime
if os.path.basename(os.path.abspath(os.path.curdir)) == 'server':
    sys.path.append('.')
    os.chdir('../../../')
from collections import deque
from socket import *
from model.chat_dto import ChatDto
from util import utils
from network import settings
from network.database.server.session.session import Session
from network.database.client.db_client import DbClient
from network.chat.server.chat_room_repository import ChatRoomMemoryRepository
from network.chat.server.mailbox import MailBox
import threading, time

session = Session()
dbClient = DbClient()
chatRoomRepository = ChatRoomMemoryRepository()
mailbox = MailBox()

send_q = deque([])
IP = gethostbyname(gethostname())
POST = settings.CHAT_PORT

usermap = {} # key : h_userid / value : socket
address_usermap = {} # key : fileno / value : h_userid


class ChattingServer:
    _server_socket = None
    _IP = IP
    _PORT = PORT
    _LISTENING_NUM = 100

    def __init__(self):
        self._server_socket = socket(AF_INET, SOCK_STREAM)

    def set_address(self, ip:str, port:int):
        self._IP = ip
        self._PORT = port

    def start_listening(self):
        self._server_socket.bind((self._IP, self._PORT))
        self._server_socket.listen(self._LISTENING_NUM)
        print(f'chatting server open from {self._IP}:{self._PORT}')
        t_send = threading.Thread(target=self.send, args=(usermap, send_q))
        t_send.start()

        while True:
            conn, addr = self._server_socket.accept()
            # TODO : set timeout here
            session_id = conn.recv(1024).decode('utf-8')

            if settings.IS_RUNNING_TOGETHER:
                h_userid = session.getHashedUserid(session_id)
            else:
                h_userid = dbClient.getUserHashedIdBySessionKey(session_id)

            if not h_userid:
                conn.close()
                continue

            t_sendMailBox = threading.Thread(target=self.sendFromMailBox, args=(h_userid, conn))
            t_sendMailBox.start()

            t_recv = threading.Thread(target=self.recv, args=(conn, send_q))
            t_recv.start()

    def sendFromMailBox(self, h_userid, conn):
        while True:
            chatdto = mailbox.pop(h_userid)
            if chatdto is None:
                break
            data = chatdto.toJson().encode('utf-8')
            conn.send(data)
        usermap[h_userid] = conn
        address_usermap[conn.fileno()] = h_userid
        print(f'connect from: {conn.getpeername()}')

    def send(self, usermap:dict, send_q):
        print('Thread Send Start')
        while True:
            try:
                if not send_q:
                    continue
                data, conn = send_q.pop()

                if data == 'close':
                    try:
                        self.disconnect(conn)
                    except Exception as e:
                        print(f'disconnect failed from {conn.getpeername()}', e)
                    continue

                chatdto:ChatDto = ChatDto.fromJson(data)

                if not chatdto:
                    self.disconnect(conn)
                    print(f'wrong data from {conn.getpeername()}')
                    continue

                if settings.IS_RUNNING_TOGETHER:
                    userlist = chatRoomRepository.getHashedUseridList(chatdto.chatRoomId)
                else:
                    userlist = dbClient.getMembersHashedUserid(chatdto.chatRoomId)

                userlist.remove(chatdto.h_userid)

                if not isinstance(userlist, list):
                    print('send failed: does not exist')
                    continue
                for hid in userlist:
                    receiver = usermap.get(hid)
                    if receiver is None:
                        mailbox.push(hid, chatdto)
                        continue
                    try:
                        receiver.send(data.encode('utf-8'))
                    except ConnectionAbortedError or ConnectionResetError:
                        mailbox.push(hid, chatdto)
                        self.disconnect(conn)
                        continue

            except Exception as e:
                print(e)

    def disconnect(self, conn):
        h_userid = address_usermap.get(conn.fileno())
        if conn.fileno() != -1:
            address_usermap.pop(conn.fileno())
        if h_userid:
            usermap.pop(h_userid)
        conn.close()
        conn.detach()


def run_chatting_server():
    global chatting_server
    chatting_server = ChattingServer()
    chatting_server.start_listening()
    mailbox.save_as_file()


if __name__ == '__main__':
    run_chatting_server()
