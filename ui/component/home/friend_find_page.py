from ui.component.scrollpage import ScrollPage
from ui.component.home.friend_find_list_item import FriendFindListItem


class FriendFindPage(ScrollPage):
    infoes = []
    items = []
    addFriendCbk = None

    def __init__(self, parent=None, infoes=[]):
        super(FriendFindPage, self).__init__(parent)
        FriendFindListItem.SIGNAL.ADD.connect(self.addFriendCbk)
        self.infoes = infoes

    def updateList(self, infoes):
        self.removeAll()
        self.items.clear()
        if isinstance(infoes, list):
            self.infoes = infoes

            for i in range(len(self.infoes)):
                listitem = FriendFindListItem(self.infoes[i])
                self.items.append(listitem)

                self.addWidget(self.items[i])
