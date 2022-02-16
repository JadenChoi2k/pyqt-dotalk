import sys
sys.path.append('../../../')
import requests, json
from model.user_info_dto import UserInfoDto
from model.user import User
from model.user_join_form import UserJoinForm
from model.user_login_form import UserLoginForm
from model.chat_room import ChatRoom
from network import settings


class DbClient:
    # singleton
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    _IP:str = None
    _PORT:int = None
    _sessionId = None
    _user:User = None

    def __init__(self):
        self._IP = settings.DB_IP
        self._PORT = settings.DB_PORT

    def setAddress(self, ip:str, port:int):
        self._IP = ip
        self._PORT = port

    def isLogin(self):
        return self._sessionId is not None

    def _getUrl(self):
        return f'http://{self._IP}:{self._PORT}'

    def getSessionId(self):
        return self._sessionId

    def isoverlap(self, userid:str)->bool:
        url = self._getUrl() + '/user/isoverlap'
        headers = {'Content-Type':'text/plain; charset=utf-8'}
        data = f'userid={userid}'
        resp = requests.get(url=url, headers=headers, data=data)
        resp_data = resp.json()
        if resp_data.get('result') == 'bad-request':
            print(resp_data.get('error'))
        return resp_data.get('isoverlap')

    def getUserFromServer(self):
        if self._sessionId is None:
            return None
        url = self._getUrl() + '/user/me'
        headers = {'Content-Type':'application/json; charset=utf-8', 'Session-ID':self._sessionId}
        resp = requests.get(url=url, headers=headers)
        resp_data = resp.json()
        if resp_data.get('status') != 200:
            return None
        else:
            user = User.fromJson(resp_data.get('user'))
            self._user = user
            return user

    def getFriendsFromServer(self):
        if self._sessionId is None:
            return None
        url = self._getUrl() + '/friends'
        headers = {'Content-Type':'application/json; charset=utf-8', 'Session-ID':self._sessionId}
        resp = requests.get(url=url, headers=headers)
        resp_data = resp.json()
        return [UserInfoDto.fromJson(friend) for friend in resp_data.get('friends')]

    def searchUserByName(self, name):
        url = self._getUrl() + '/info/byname'
        headers = {'Content-Type':'application/json; charset=utf-8'}
        resp = requests.get(url=url, headers=headers, data=name.encode('utf-8'))
        resp_data = resp.json()
        if resp_data.get('found'):
            users = [UserInfoDto.fromJson(json_u) for json_u in resp_data.get('data')]
            return users
        else:
            return None

    def addFriendByHashedUserid(self, h_userid):
        if self._user is None:
            return None
        url = self._getUrl() + '/friends/add'
        headers = {'Content-Type':'application/json; charset=utf-8', 'Session-ID':self._sessionId}
        resp = requests.post(url=url, headers=headers, data=h_userid.encode('utf-8'))
        resp_data = resp.text
        if resp_data == 'ok':
            return True
        else:
            return False

    def getUser(self)->User:
        return self._user

    def getUserHashedIdBySessionKey(self, sessionKey):
        url = self._getUrl() + '/user/hashid'
        headers = {'Content-Type':'text/plain; charset=utf-8', 'Session-ID':sessionKey}
        resp = requests.get(url=url, headers=headers)
        if resp.status_code == 200:
            return resp.text
        else:
            return None

    def getChatRooms(self):
        url = self._getUrl() + '/user/chat'
        headers = {'Content-Type':'application/json; charset=utf-8', 'Session-ID':self._sessionId}
        resp = requests.get(url=url, headers=headers)
        if resp.status_code == 200:
            resp_data = resp.json()
            rooms = [ChatRoom.fromJson(jstr) for jstr in resp_data.get('result')]
            return rooms
        return None

    def getChatRoomById(self, roomid:str)->ChatRoom:
        url = self._getUrl() + '/chat/byroomid'
        headers = {'Content-Type':'application/json; charset=utf-8'}
        resp = requests.get(url=url, headers=headers, data=roomid.encode('utf-8'))
        if resp.status_code == 200:
            resp_data = ChatRoom.fromJson(resp.text)
            return resp_data
        return None

    def doChatOneRoom(self, friend_hid:str):
        url = self._getUrl() + '/chat/one-to-one'
        headers = {'Content-Type':'text/plain; charset=utf-8', 'Session-ID':self._sessionId}
        resp = requests.get(url=url, headers=headers, data=friend_hid.encode('utf-8'))
        if resp.status_code == 200:
            return resp.text
        return None

    def createNewChatroom(self, userlist:list):
        url = self._getUrl() + '/chat/new'
        headers = {'Content-Type':'application/json; charset=utf-8', 'Session=ID':self._sessionId}
        data = '&'.join(userlist)
        resp = requests.post(url=url, headers=headers, data=data.encode('utf-8'))
        if resp.status_code != 400:
            resp_data = resp.text
            chatroom = ChatRoom.fromJson(resp_data)
            return chatroom
        return None

    def getMembersHashedUserid(self, roomid):
        url = self._getUrl() + '/chat/members/hashid'
        headers = {'Content-Type':'text/plain; charset=utf-8'}
        data = roomid
        resp = requests.get(url=url, headers=headers, data=data.encode('utf-8'))
        if resp.status_code == 200:
            return resp.text.split('&')
        return resp.text

    def addMemberToChatRoom(self, roomid, userlist:list):
        url = self._getUrl() + '/chat/addMember'
        headers = {'Content-Type':'text/plain; charset=utf-8', 'Session-ID':self._sessionId}
        data = f'{roomid}&' + '&'.join(userlist)
        resp = requests.post(url=url, headers=headers, data=data.encode('utf-8'))
        if resp.status_code == 201:
            return True
        return False

    # returns (success?, result)
    def join(self, form:UserJoinForm)->tuple:
        url = self._getUrl() + '/user/join'
        headers = {'Content-Type':'application/json; charset=utf-8'}
        data = form.toJson()
        resp = requests.post(url=url, headers=headers, data=data)
        resp_data = resp.json()
        result = resp_data.get('result') == 'success'
        if result:
            return result, 'success'
        else:
            return result, resp_data.get('error-code')

    def login(self, form:UserLoginForm):
        url = self._getUrl() + '/user/login'
        headers = {'Content-Type':'application/json; charset=utf-8'}
        data = form.tojson()
        resp = requests.post(url=url, headers=headers, data=data)
        resp_data = resp.json()
        self._sessionId = resp.headers.get('Session-ID')
        result = resp_data.get('result') == 'success'
        if result:
            return True, resp_data.get('username')
        else:
            return False, resp_data.get('error-code')
