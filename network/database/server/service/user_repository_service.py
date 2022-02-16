import uuid
from network.database.server.repository.user_memory_repository import UserMemoryRepository
from model.user import User
from model.user_join_form import UserJoinForm
from model.user_login_form import UserLoginForm
from model.validator.user_join_form_validator import UserJoinFormValidator

join_validator = UserJoinFormValidator()
repository = UserMemoryRepository()
join_message = {'type-error':'internal error'}


class UserRepositoryService:

    def login(self, form:UserLoginForm):
        user = repository.findByUserid(form.userid)
        if user is None:
            return False, 'wrong login id'
        if user.get_password() == form.password:
            return str(uuid.uuid1()), user.get_userid(), user.get_name()
        else:
            return False, 'wrong password'

    def join(self, form:UserJoinForm):
        valid = join_validator.valid(form)
        if isinstance(valid, tuple):
            if valid[0] == True:
                user = self.createUserFromForm(form)
                user = repository.save(user)
                if user is None:
                    return 'overlapped userid'
                else:
                    return user
            else:
                return valid[1]
        else:
            return 'type-error'

    def isoverlap(self, userid:str):
        user = repository.findByUserid(userid)
        if user:
            return True
        else:
            return False

    def isExistHashedUserid(self, hid):
        return repository.isExistHashedUserid(hid)

    def findByName(self, q:str)->list:
        return [info.toJson() for info in repository.findByName(q)]

    def addFriend(self, my_userid, h_userid):
        return repository.addFriendByHashedUserid(my_userid, h_userid)

    def getInfoByHashedUserid(self, hid):
        return repository.findInfoByHashedUserid(hid)

    def getFriends(self, my_userid):
        return [info.toJson() for info in repository.getFriendsInfoByUserid(my_userid)]

    def createUserFromForm(self, form:UserJoinForm)->User:
        return User(
            userid=form.userid,
            password=form.password,
            name=form.name,
            department=form.department,
            position=form.position,
            birth=form.birth,
            signup_date=form.signup_date,
            color=form.color
        )

    def save_repository(self):
        repository.save_as_file()
