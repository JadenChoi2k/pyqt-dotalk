from util import utils
from ui.component.scrollpage import ScrollPage
from model.chat_dto import ChatDto
from pages.chatting.chatting_room_context import ChattingRoomContext
from network.database.client.db_client import DbClient
import os
import preferences
from ui.component.home.chat_list_item import ChatListItem


class ChattingHomePage(ScrollPage):
    chat_widgets_list:list = []
    list_widgets:dict = {} # roomid : chatListItem
    chat_context:ChattingRoomContext = None

    def __init__(self, parent=None):
        super(ChattingHomePage, self).__init__(parent)
        self.initChattingContext()

    def initUI(self):
        pass

    def initChattingContext(self):
        self.chat_context = ChattingRoomContext.fromChattingLog()
        self.chat_context.SIGNALS.SEND.connect(self.addChatByDto)
        self.chat_context.SIGNALS.RECEIVED.connect(self.addChatByDto)
        self.chat_context.SIGNALS.READ.conntext(self.readChat)
        self.chat_context.SIGNALS.UPDATE_ROOM.connect(self.changeChatName)
        self.chat_context.updateChatRoomNames()
        self.chat_context.connect_server()

    def addChatByDto(self, dto:ChatDto):
        w:ChatListItem = self.list_widgets.get(dto.chatRoomId)
        if w:
            self.setFirstByWidget(w)
            w.setLastChat(dto)
            w.setReadNum(w.read_num + 1)
        else:
            cli = ChatListItem()
            cli.setRoomid(dto.chatRoomId)
            cli.clicked_cbk.connect(self.doChat)
            cli.setLastChat(dto)
            cli.setChatName(self.chat_context.getChatRoomNameById(dto.chatRoomId))
            cli.setReadNum(1)
            self.appendFirst(cli)

    def readChat(self, roomid):
        w:ChatListItem = self.list_widgets.get(roomid)
        if w:
            w.setReadNum(0)
            return True
        else:
            return False

    def appendFirst(self, widget):
        self.chat_widgets_list.insert(0, widget)
        self.list_widgets[widget.roomid] = widget
        self.insertWidget(0, widget)

    def setFirstByWidget(self, widget):
        try:
            index = self.chat_widgets_list.index(widget)
            self.setFirstByIndex(index)
        except ValueError:
            print('could not find chat')

    def setFirstByIndex(self, index):
        if index >= len(self.chat_widgets_list):
            return
        tmp = self.chat_widgets_list[index]
        self.chat_widgets_list.remove(tmp)
        self.removeAt(index)
        self.appendFirst(tmp)

    def updateState(self):
        self.removeAll()
        for w in self.chat_widgets_list:
            if isinstance(w, ChatListItem) and hasattr(w, 'roomid') and w.roomid:
                self.list_widgets[w.roomid] = w
                self.addWidget(w)

    def changeChatName(self, roomid, name):
        item = self.list_widgets.get(roomid)
        if isinstance(item, ChatListItem):
            item.setChatName(name)
            return True

    def removeByRoomid(self, roomid):
        w = self.list_widgets.get(roomid)
        if w:
            self.removeWidget(w)
            self.list_widgets.pop(roomid)
            return True
        return False

    def doChat(self, roomid):
        self.chat_context.openChattingRoom(roomid)

    def _saveListItemsAsFile(self):
        if not os.path.isdir(preferences.CHAT_LIST_SAVE_PATH):
            os.mkdir(preferences.CHAT_LIST_SAVE_PATH)
        huserid = DbClient().getUser().get_hashed_userid()
        userpath = os.path.join(preferences.CHAT_LIST_SAVE_PATH, utils.filter_window_path(huserid))

        if not os.path.isdir(userpath):
            os.mkdir(userpath)

        filepath = os.path.join(userpath, 'chatlist.items')
        with open(filepath, 'wt') as f:
            for idx, w in enumerate(self.chat_widgets_list):
                try:
                    f.write(w.toJson() + '\n')
                except Exception as e:
                    print('chat list item parse failed - seq', idx, e)
        print('saving chatting list item succeeded')

    @staticmethod
    def fromFile():
        huserid = DbClient().getUser().get_hashed_userid()
        srcpath = os.path.join(preferences.CHAT_LIST_SAVE_PATH, utils.filter_window_path(huserid), 'chatlist.items')

        page = ChattingHomePage()
        if not os.path.isfile(srcpath):
            return page

        list_widgets = []
        with open(srcpath, 'rt') as f:
            for idx, line in enumerate(f.readlines()):
                try:
                    list_widget = ChatListItem.fromJson(line.strip())
                    list_widget.clicked_cbk.connect(page.doChat)
                    list_widgets.append(list_widget)
                except:
                    print('chatting list items load failed')
        print('chatting list items loaded from file')
        page.chat_widgets_list = list_widgets
        page.updateState()
        page.chat_context.updateChatRoomNames()
        return page

    def closeEvent(self, e):
        self.chat_context.closeConnection()
        self._saveListItemsAsFile()
