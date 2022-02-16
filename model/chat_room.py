import uuid, os
import json
from model.chat_dto import ChatDto
from model.user_info_dto import UserInfoDto


class ChatRoom:
    _roomid = None
    name = None
    _users = None # key : h_userid / value : userinfo
    chattings = None # list of chat_dto

    def __init__(self):
        self._roomid = str(uuid.uuid1())
        self.name = None
        self._users = {}
        self.chattings = []

    def addUser(self, userinfo:UserInfoDto):
        if isinstance(userinfo, UserInfoDto):
            self._users.update([[userinfo.h_userid, userinfo]])
        else:
            print('[ChatRoom.addUser] UserInfoDto type needed')

    def addUsers(self, users):
        if isinstance(users, list):
            for user in users:
                self.addUser(user)
        else:
            print('[ChatRoom.addUsers] list type needed')

    def removeUserByHashedUserid(self, h_userid)->UserInfoDto:
        return self._users.pop(h_userid)

    def getUserByHashedUserid(self, h_userid)->UserInfoDto:
        return self._users.get(h_userid)

    def getRoomid(self):
        return self._roomid

    def setName(self, name):
        if name is None or name == '':
            return None
        self.name = name
        return self.name

    def getName(self, my_hid=None):
        if not self.name:
            if len(self._users) == 2 and my_hid:
                hid = list(self._users.keys())
                hid.remove(my_hid)
                friend_hid = hid[0]
                return self._users[friend_hid].name

            defaultname = ', '.join([u.name for u in self._users.values() if hasattr(u, 'name')])
            if len(defaultname) > 12:
                return defaultname[:12] + f'... ({len(self._users)})'
            return defaultname
        else:
            return self.name + f' ({len(self._users)})'

    def getUsers(self):
        return self._users

    def getUserHashedIdList(self):
        return list(self._users.keys())

    def setUsers(self, users:dict):
        if isinstance(users, dict):
            self._users = users

    def addChat(self, chatdto:ChatDto):
        if isinstance(chatdto, ChatDto):
            self.chattings.append(chatdto)

    def getLastChatsByNumber(self, num):
        return self.chattings[-num:]

    def getWholeChat(self):
        return self.chattings

    def toJson(self):
        dic = {}
        dic['roomid'] = self._roomid
        dic['name'] = self.name
        dic['users'] = {hid: uinfo.toJson() for hid, uinfo in self._users.items()}
        dic['chattings'] = [c.toJson() for c in self.chattings]

    def fromJson(data):
        dic = json.loads(data)
        ret = ChatRoom()
        ret._roomid = dic.get('roomid')
        ret.name = dic.get('name')
        ret.setUsers({hid: UserInfoDto.fromJson(uinfo) for hid, uinfo in dic.get('users').items()})
        ret.chattings = [ChatDto.fromJson(c) for c in dic.get('chattings')]
        return ret

    # load from local file by room id
    def fromLocalData(roomid):
        rootpath = '../pages/chatting/chatlog'
        logpath = os.path.join(rootpath, roomid, 'chat.log')
        if not os.path.exists(logpath):
            return None
        pass
