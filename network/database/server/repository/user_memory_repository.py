from util import utils
from model.user import User
from model.user_info_dto import UserInfoDto
from network import settings
import os


class UserMemoryRepository(object):
    # singleton
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    _users:dict = {} # id : user
    _friends:dict = {} # id : list(friend_id)
    _userid:dict = {} # userid : id
    _userhid:dict = {} # h_userid : id
    seq:int = 0

    def save(self, user:User):
        isoverlap = self.findByUserid(user.get_userid())
        if isoverlap is not None:
            return None
        if user.get_id() is None:
            self.seq += 1
            user.set_id(self.seq)
        self._users[user.get_id()] = user
        self._userid[user.get_userid()] = user.get_id()
        self._userhid[str(utils.hashDigest(user.get_userid()))] = user.get_id()
        return user

    def findInfoByHashedUserid(self, hid):
        _id = self._userid.get(hid)
        user = self._users[_id]
        return UserInfoDto.fromUser(user)

    def isExistHashedUserid(self, hid):
        return self._userhid.get(hid) is not None

    def findByUserid(self, userid)->User:
        _id = self._userid.get(userid)
        return self._users.get(_id)

    def findById(self, id:int)->User:
        return self._users.get(id)

    def findAll(self):
        return list(self._users.values())

    def patchWhole(self, new_user:User):
        user = self.findByUserid(new_user.get_userid())
        new_user.set_id(user.get_id())
        self._users[user.get_userid()] = new_user
        return True

    def patchAttr(self, userid, field, new_value):
        user = self.findByUserid(userid)
        if not user:
            return None
        if field[0] != '_':
            field = '_' + field
        if hasattr(user, field):
            try:
                if field in ['_id', '_userid', '_birthday', '_signup_date']:
                    raise ValueError('this field can not be changed')
                getattr(user, f'set{field}')(new_value)
            except Exception as e:
                print(e)
        return user

    def deleteByUserid(self, userid):
        user = self.findByUserid(userid)
        if user is None:
            return None
        self._userid.pop(user.get_userid())
        self._userhid.pop(utils.hashDigest(user.get_userid()))
        return self._users.pop(user.get_id())

    def deleteById(self, id:int):
        user = self.findByUserid(id)
        if user is None:
            return None
        self._userid.pop(user.get_userid())
        self._userhid.pop(utils.hashDigest(user.get_userid()))
        return self._users.pop(user.get_id())

    def addFriendByHashedUserid(self, my_userid, h_userid):
        my_id = self._userid.get(my_userid)
        friend_id = self._userhid.get(h_userid)

        if not my_id or not friend_id:
            return None

        if my_id == friend_id:
            return False

        friends = self._friends.get(my_id)
        if not friends:
            self._friends[my_id] = [friend_id]
        else:
            if friend_id in friends:
                return False
            friends.append(friend_id)
        return True

    def getFriendsInfoByUserid(self, userid):
        infoes = []
        my_id = self._userid.get(userid)
        friends_ids = self._friends.get(my_id)
        if isinstance(friends_ids, list):
            for friends_id in friends_ids:
                friend = self.findById(friends_id)
                infoes.append(UserInfoDto.fromUser(friend))
        return infoes

    def findByName(self, q:str):
        result = []
        for u in self.findAll():
            if q in u.get_name():
                result.append(UserInfoDto.fromUser(u))
        return result

    def save_as_file(self):
        if not os.path.isdir(settings.DB_FILE_PATH):
            return None

        with open(os.path.join(settings.DB_FILE_PATH, settings.DB_USER_FILE_NAME), 'wt') as f:
            f.write(str(self.seq) + '\n')
            for user in self._users.values():
                f.write(user.toJsonFull() + '\n')
        with open(os.path.join(settings.DB_FILE_PATH, settings.DB_FRIEND_FILE_NAME), 'wt') as f:
            for me_id, friend_id in self._friends.items():
                if isinstance(friend_id, list):
                    line = f"{me_id}, {', '.join(map(str, friend_id))}"
                    f.write(line + '\n')
        print('UserMemoryRepository saved as file')

    @staticmethod
    def from_file():
        user_path = os.path.join(settings.DB_FILE_PATH, settings.DB_USER_FILE_NAME)
        friend_path = os.path.join(settings.DB_FILE_PATH, settings.DB_FRIEND_FILE_NAME)
        repository = UserMemoryRepository()

        try:
            with open(user_path, 'rt') as f:
                seq = int(f.readline())
                for line in f.readlines():
                    if not line:
                        continue
                    user = User.fromJson(line.strip())
                    repository.save(user)
                repository.seq = seq
            with open(friend_path, 'rt') as f:
                for line in f.readlines():
                    if not line:
                        continue
                    ids = list(map(int, line.split(',')))
                    repository._friends[ids[0]] = ids[1:]
            return repository
        except Exception as e:
            print('UserMemoryRepository load failed', e)
            return UserMemoryRepository()
