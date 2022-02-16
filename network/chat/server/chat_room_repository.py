from model.chat_room import ChatRoom
from network import settings
from network.database.server.repository.user_memory_repository import UserMemoryRepository
import os

user_repository = UserMemoryRepository()


class ChatRoomMemoryRepository:
    # singleton
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    rooms = {} # roomid : chat room
    oneroom = {} # h_userid : {h_userid : roomid}
    usermap = {} # h_userid : list(roomid)

    def _addRoomidToUsers(self, roomid, h_userid):
        roomlist = self.usermap.get(h_userid)
        if roomlist is None:
            self.usermap[h_userid] = [roomid]
        else:
            roomlist.append(roomid)

    def _removeRoomidFromUsers(self, roomid, h_userid):
        roomlist = self.usermap.get(roomid)
        if roomlist is None:
            return None
        try:
            roomlist.remove(roomid)
            return True
        except ValueError:
            return False

    def addChatRoom(self, chatRoom:ChatRoom):
        roomid = chatRoom.getRoomid()
        user_hids:list = list(chatRoom.getUsers().keys())

        self.rooms[roomid] = chatRoom

        if len(user_hids) == 2:
            my_room = self.oneroom.get(user_hids[0])
            friend_room = self.oneroom.get(user_hids[1])

            if not isinstance(my_room, dict):
                self.oneroom[user_hids[0]] = {user_hids[1] : roomid}
            else:
                my_room[user_hids[1]] = roomid

            if not isinstance(friend_room, dict):
                self.oneroom[user_hids[1]] = {user_hids[0] : roomid}
            else:
                friend_room[user_hids[0]] = roomid

        for hid in user_hids:
            self._addRoomidToUsers(roomid, hid)

    def getRoomByRoomid(self, roomid):
        return self.rooms.get(roomid)

    def getOneToOneChatRoom(self, my_hid, friend_hid):
        my_oneroom: dict = self.oneroom.get(my_hid)
        roomid = None

        if isinstance(my_oneroom, dict):
            roomid = my_oneroom.get(friend_hid)

        if not roomid or not my_oneroom:
            room = ChatRoom()
            my_info = user_repository.findInfoByHashedUserid(my_hid)
            friend_info = user_repository.findInfoByHashedUserid(friend_hid)
            if not friend_info or not my_info:
                raise ValueError('requested user does not exist')
            room.addUser(my_info)
            room.addUser(friend_info)
            self.addChatRoom(room)
            roomid = room.getRoomid()

        return roomid

    def addChatUser(self, roomid, h_userid):
        room = self.rooms.get(roomid)
        if room is None:
            return False
        room.addUser(h_userid)
        self._addRoomidToUsers(roomid, h_userid)

    def removeChatUser(self, roomid, h_userid):
        room = self.rooms.get(roomid)
        if room is None:
            return False
        room.removeUser(h_userid)

    def getHashedUseridList(self, roomid):
        room: ChatRoom = self.rooms.get(roomid)
        if room is None:
            return False
        return room.getUserHashedIdList()

    def getRoomsByHashedUserid(self, h_userid):
        roomids = self.usermap.get(h_userid)
        if not roomids:
            return None
        ret = []
        for roomid in roomids:
            room = self.getRoomByRoomid(roomid)
            if room: ret.append(room)
        return ret

    def save_as_file(self):
        if not os.path.isdir(settings.CHAT_DB_FILE_PATH):
            return None
        roompath = os.path.join(settings.CHAT_DB_FILE_PATH, settings.CHAT_ROOM_ROOMS_FILE_NAME)
        usermappath = os.path.join(settings.CHAT_DB_FILE_PATH, settings.CHAT_ROOM_USERMAP_FILE_NAME)
        oneroompath = os.path.join(settings.CHAT_DB_FILE_PATH, settings.CHAT_ROOM_ONEROOM_FILE_NAME)

        try:
            with open(roompath, 'wt', encoding='utf-8') as f:
                for room in self.rooms.values():
                    f.write(room.toJson() + '\n')

            with open(usermappath, 'wt', encoding='utf-8') as f:
                for hid, roomids in self.usermap.items():
                    f.write(hid + '\n')
                    f.write(','.join(roomids) + '\n')

            with open(oneroompath, 'wt', encoding='utf-8') as f:
                for my_hid, oneroom in self.oneroom.items():
                    f.write(my_hid + '\n')
                    f.write(str(len(oneroom)) + '\n')
                    if isinstance(oneroom, dict):
                        for f_hid, roomid in oneroom.items():
                            f.write(f_hid + ' : ' + roomid + '\n')

            print('saving ChatRoomRepository succeeded')

        except Exception as e:
            print('saving ChatRoomRepository failed', e)

    def from_file():
        if not os.path.isdir(settings.CHAT_DB_FILE_PATH):
            return ChatRoomMemoryRepository()

        roompath = os.path.join(settings.CHAT_DB_FILE_PATH, settings.CHAT_ROOM_ROOMS_FILE_NAME)
        usermappath = os.path.join(settings.CHAT_DB_FILE_PATH, settings.CHAT_ROOM_USERMAP_FILE_NAME)
        oneroompath = os.path.join(settings.CHAT_DB_FILE_PATH, settings.CHAT_ROOM_ONEROOM_FILE_NAME)

        if not os.path.isfile(roompath) or not os.path.isfile(usermappath) or not os.path.isfile(oneroompath):
            return ChatRoomMemoryRepository()

        try:
            repository = ChatRoomMemoryRepository()
            # load from file
            with open(roompath, 'rt', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    if not line:
                        continue
                    room = ChatRoom.fromJson(line.strip())
                    repository.addChatRoom(room)
            with open(usermappath, 'rt', encoding='utf-8') as f:
                lines = f.readlines()
                for i in range(0, len(lines), 2):
                    hid = lines[i]
                    roomids = lines[i + 1].strip().split(',')
                    repository.usermap.update([[hid, roomids]])
            with open(oneroompath, 'rt', encoding='utf-8') as f:
                oneroom = {}
                lines = f.readlines()

                idx = 0
                while idx < len(lines):
                    my_hid = lines[idx].strip()
                    oneroom[my_hid] = {}
                    idx += 1
                    room_num = int(lines[idx])
                    idx += 1
                    for _ in range(room_num):
                        line = lines[idx]
                        sep_idx = line.rfind(':')
                        f_hid = line[:sep_idx].strip()
                        roomid = lines[sep_idx + 1:].strip()
                        oneroom[my_hid][f_hid] = roomid
                        idx += 1

            return repository
        except Exception as e:
            print('ChatRoomRepository load from file failed', e)
            return ChatRoomMemoryRepository()
