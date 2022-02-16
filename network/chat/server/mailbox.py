from collections import deque
from model.chat_dto import ChatDto
from network import settings
import os


class MailBox:
    # singleton
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    _mailbox = {} # h_userid : chat_dto

    def push(self, h_userid, dto:ChatDto):
        dtolist = self._mailbox.get(h_userid)
        if dtolist is None:
            self._mailbox[h_userid] = deque([])
        self._mailbox[h_userid].appendleft(dto)

    def pop(self, h_userid):
        dtolist = self._mailbox.get(h_userid)
        if not dtolist:
            return None
        return dtolist.pop()

    def save_as_file(self):
        if not os.path.isdir(settings.CHAT_DB_FILE_PATH):
            return None

        dest_path = os.path.join(settings.CHAT_DB_FILE_PATH, settings.CHAT_MAILBOX_FILE_NAME)
        with open(dest_path, 'wt', encoding='utf-8') as f:
            for hid, chatq in self._mailbox.items():
                if not isinstance(chatq, deque):
                    continue
                chat_list = list(chatq)
                f.write(hid + '\n')
                f.write(str(len(chat_list)) + '\n')
                while chat_list:
                    chat:ChatDto = chat_list.pop()
                    if isinstance(chat, ChatDto):
                        f.write(chat.toJson() + '\n')
                    else:
                        f.write('\n')
        print('mailbox saved successfully')

    @staticmethod
    def from_file():
        src_path = os.path.join(settings.CHAT_DB_FILE_PATH, settings.CHAT_MAILBOX_FILE_NAME)
        mailbox = MailBox()
        if not os.path.isfile(src_path):
            return mailbox

        try:
            with open(src_path, 'rt', encoding='utf-8') as f:
                lines = f.readlines()
                idx = 0

                while idx < len(lines):
                    chatq = deque()
                    hid = lines[idx].strip()
                    idx += 1
                    chat_num = int(lines[idx])
                    idx += 1

                    for _ in range(chat_num):
                        chatjson = lines[idx].strip()
                        if chatjson:
                            chat = ChatDto.fromJson(chatjson)
                            chatq.appendleft(chat)
                        idx += 1
                    mailbox._mailbox[hid] = chatq
                return mailbox

        except Exception as e:
            print('mailbox load from file failed', e)
            return MailBox()
