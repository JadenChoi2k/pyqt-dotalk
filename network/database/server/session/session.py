from network.database.server.repository.user_memory_repository import UserMemoryRepository
from util import utils

repository = UserMemoryRepository()


class Session:
    # singleton
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    session = {} # uuid : userid
    inverse_session = {} # userid : uuid

    def add(self, uuid, userid)->bool:
        try:
            old_uuid = self.inverse_session.get(userid)
            if old_uuid:
                self.session.pop(old_uuid, None)
                self.inverse_session.pop(userid, None)
            self.session[uuid] = userid
            self.inverse_session[userid] = uuid
            return True
        except Exception as e:
            print('Session add failed', e)
            return False

    def get(self, uuid):
        userid = self.session.get(uuid)
        user = repository.findByUserid(userid)
        return user

    def getUserid(self, uuid):
        return self.session.get(uuid)

    def getHashedUserid(self, uuid):
        userid = self.getUserid(uuid)
        if userid is None:
            return None
        else:
            return str(utils.hashDigest(userid))

    def exists(self, uuid):
        return self.session.get(uuid) is not None
