import os, sys, threading
if os.path.basename(os.path.abspath(os.path.curdir)) == 'network':
    sys.path.append('.')
    os.chdir('..')
from network import settings
settings.IS_RUNNING_TOGETHER = True

from network.chat.server import chatting_server
from network.database.server import db_server
from network.database.server.repository.user_memory_repository import UserMemoryRepository
from network.chat.server.mailbox import MailBox
from network.chat.server.chat_room_repository import ChatRoomMemoryRepository
from util import utils

# chatting server and db server run on one context
user_repository = UserMemoryRepository.from_file()
mailbox = MailBox.from_file()
chat_room_repository = ChatRoomMemoryRepository.from_file()

def save_as_file():
    user_repository.save_as_file()
    mailbox.save_as_file()
    chat_room_repository.save_as_file()

def run_server():
    threading.Thread(target=db_server.run_db_server).start()
    threading.Thread(target=chatting_server.run_chatting_server).start()


if __name__ == '__main__':
    utils.RepeatedTimer(600, save_as_file)
    run_server()
