from PyQt5 import QtCore
from model.user import User
from model.user_info_dto import UserInfoDto
from network.database.client.db_client import DbClient

dbClient = DbClient()


class UserInfoContextSignals(QtCore.QObject):
    UPDATE = QtCore.pyqtSignal()


class UserInfoContext:
    # singleton
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    _me:User = None
    _friends:list = []
    SIGNALS = UserInfoContextSignals()

    def initInfo(self):
        self.setMeFromServer()
        self.setFriendsFromServer()
        self.SIGNALS.UPDATE.emit()

    def getMe(self):
        return self._me

    def getMyInfo(self):
        if isinstance(self._me, User):
            return UserInfoDto.fromUser(self._me)

    def getFriendsInfo(self):
        return self._friends

    def isFriend(self, h_userid):
        return h_userid in [info.h_userid for info in self.getFriendsInfo()]

    def setMeFromServer(self):
        self._me = dbClient.getUserFromServer()

    def setMe(self):
        self._me = dbClient.getUser()

    def setFriendsFromServer(self):
        self._friends = dbClient.getFriendsFromServer()

    def addFriendByHashedUserid(self, friend_hid):
        result:bool = dbClient.addFriendByHashedUserid(friend_hid)
        if result:
            self.setFriendsFromServer()
            self.SIGNALS.UPDATE.emit()
        return result
