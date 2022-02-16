import sys, socket, os, datetime

if os.path.basename(os.path.abspath(os.path.curdir)) == 'server':
    sys.path.append('db_server.py')
    os.chdir('../../../')

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from model.user import User
from model.user_login_form import UserLoginForm
from model.user_join_form import UserJoinForm
from model.chat_room import ChatRoom
from network.database.server.session.session import Session
from network.database.server.service.user_repository_service import UserRepositoryService
from network.chat.server.chat_room_repository import ChatRoomMemoryRepository

IP = socket.gethostbyname(socket.gethostname())
PORT = 9999

session = Session()
user_repo_service = UserRepositoryService()
chat_room_repo = ChatRoomMemoryRepository()


class DbHTTPRequestHandler(BaseHTTPRequestHandler):
    '''
    GET MAPPING
    '''

    def _users(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write('ok'.encode('utf-8'))

    def _isoverlap(self):
        content_length = int(self.headers.get('Content-Length'))
        body = self.rfile.read(content_length).decode('utf-8')
        try:
            userid = body.split('=')[1]
            isoverlap = user_repo_service.isoverlap(userid)
            result = {'result': 'ok', 'isoverlap': isoverlap}
            self.send_response(200, 'ok')
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        except Exception as e:
            self.send_response(400, 'bad-request')
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            result = {'result': 'bad-request', 'error': str(e)}
            self.wfile.write(json.dumps(result).encode('utf-8'))

    def _user_me(self):
        result = {}
        sessionId = self.headers.get('Session-ID')
        if sessionId is None:
            self.send_response(401, 'unauthorized')
            result = {'result': 'fail', 'status': 401, 'status-message': 'unauthorized'}
        user = session.get(sessionId)
        if user is None:
            self.send_response(404, 'not-found')
            result = {'result': 'fail', 'status': 404, 'status-message': 'not-found'}
        else:
            self.send_response(200, 'ok')
            result = {'result': 'found', 'status': 200, 'status-message': 'found', 'user': user.toJson()}
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def _get_user_hid(self):
        sessionId = self.headers.get('Session-ID')
        if not sessionId:
            self.send_response(400, 'bad request')
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('400 - bad request'.encode('utf-8'))
            return
        hid = session.getHashedUserid(sessionId)

        if not hid:
            self.send_response(404, 'not found')
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('404 - not found'.encode('utf-8'))
            return
        self.send_response(200, 'ok')
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(hid.encode('utf-8'))

    def _get_my_chatroom(self):
        sessionId = self.headers.get('Session-ID')
        my_hid = session.getHashedUserid(sessionId)
        if not my_hid:
            self.send_response(401)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'result': '401 unauthorized'}).encode('utf-8'))
        else:
            rooms = [room.toJson() for room in chat_room_repo.getRoomsByHashedUserid(my_hid)]
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'result': rooms}).encode('utf-8'))

    def _get_members_huserid_in_room(self):
        try:
            content_length = int(self.headers.get('Content-Length'))
            roomid = self.rfile.read(content_length).decode('utf-8')
        except:
            self.send_response(400, 'bad request')
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('400 bad request'.encode('utf-8'))
        members = chat_room_repo.getHashedUseridList(roomid)

        if isinstance(members, list):
            self.send_response(200, 'ok')
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('&'.join(members).encode('utf-8'))
        else:
            self.send_response(404, 'not found')
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('404 not found'.encode('utf-8'))

    def _get_chatroom_by_roomid(self):
        try:
            content_length = int(self.headers.get('Content-Length'))
            roomid = self.rfile.read(content_length).decode('utf-8')
        except:
            self.send_response(400, 'bad request')
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('400 bad request'.encode('utf-8'))
            return
        room: ChatRoom = chat_room_repo.getRoomByRoomid(roomid)

        if isinstance(room, ChatRoom):
            self.send_response(200, 'ok')
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(room.toJson().encode('utf-8'))
        else:
            self.send_response(404, 'not found')
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('404 not found'.encode('utf-8'))

    def _find_by_name(self):
        try:
            content_length = int(self.headers.get('Content-Length'))
        except TypeError as e:
            print(self.address_string(), e)
            self.send_response(400)
            self.send_header('Content-Type', 'text/plaint; charset=utf-8')
            self.end_headers()
            self.wfile.write('400 Bad request. please input text'.encode('utf-8'))
            return
        searchtext = self.rfile.read(content_length).decode('utf-8')
        searchresult = user_repo_service.findByName(searchtext)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        result = {}
        if searchresult:
            result = {'found': True, 'data': searchresult}
        else:
            result = {'found': False, 'data': searchresult}
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def _do_chat_oneroom(self):
        try:
            sessionId = self.headers.get('Session-ID')
            my_hid = session.getHashedUserid(sessionId)
            content_length = int(self.headers.get('Content-Length'))
            friend_hid = self.rfile.read(content_length).decode('utf-8')
            roomid = chat_room_repo.getOneToOneChatRoom(my_hid, friend_hid)

            if not isinstance(roomid, str):
                raise TypeError('type of roomid must be string type')
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(roomid.encode('utf-8'))
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('400 Bad request'.encode('utf-8'))

    def _get_friends_of_mine(self):
        my_userid = session.getUserid(self.headers.get('Session-ID'))
        friends = user_repo_service.getFriends(my_userid)
        result = {'friends': friends}
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    '''
    POST MAPPING
    '''

    def _join(self):
        content_length = int(self.headers.get('Content-Length'))
        body = self.rfile.read(content_length).decode('utf-8')
        form = UserJoinForm.fromJson(body)
        form.signup_date = datetime.datetime.now()
        user = user_repo_service.join(form)
        if isinstance(user, User):
            self.send_response(201)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write('{"result":"success"}'.encode('utf-8'))
        else:
            error_result = {'result': 'fail', 'error-code': user}
            self.send_response(400)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

    def _login(self):
        content_length = int(self.headers.get('Content-Length'))
        body = self.rfile.read(content_length).decode('utf-8')
        form = UserLoginForm.fromJson(body)
        login = user_repo_service.login(form)
        if login[0]:
            uuid, userid, username = login
            session.add(uuid, userid)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Session-ID', uuid)
            self.end_headers()
            result = {'result': 'success', 'username': username}
            self.wfile.write(json.dumps(result).encode('utf-8'))
        else:
            result, error_code = login
            self.send_response(400)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            result = {'result': 'fail', 'error-code': error_code}
            self.wfile.write(json.dumps(result).encode('utf-8'))

    def _add_friend(self):
        try:
            content_length = int(self.headers.get('Content-Length'))
            h_userid = self.rfile.read(content_length).decode('utf-8')
            my_userid = session.getUserid(self.headers.get('Session-ID'))
            result = user_repo_service.addFriend(my_userid, h_userid)
            if result:
                self.send_response(201)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write('ok'.encode('utf-8'))
                return
        except:
            pass
        # failed
        self.send_response(400)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        if result is None:
            self.wfile.write('failed'.encode('utf-8'))
        if result is False:
            self.wfile.write('already friend'.encode('utf-8'))

    def _patch(self):
        pass

    def _create_chatting_room(self):
        sessionId = self.headers.get('Session-ID')
        my_hid = session.getHashedUserid(sessionId)
        try:
            if not my_hid:
                raise AttributeError('unauthorized user.')
            content_length = int(self.headers.get('Content-Length'))
            data = self.rfile.read(content_length).decode('utf-8')
            hids = data.split('&')
            for hid in hids:
                if not user_repo_service.isExistHashedUserid(hid):
                    raise ValueError('user does not exist')
            chatRoom = ChatRoom()
            chatRoom.setUsers({hid:user_repo_service.getInfoByHashedUserid(hid) for hid in hids})
            chatRoom.addUser(user_repo_service.getInfoByHashedUserid(my_hid))
            chat_room_repo.addChatRoom(chatRoom)

            self.send_response(201)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(chatRoom.toJson().encode('utf-8'))
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'error':str(e)}).encode('utf-8'))

    def _add_chatting_member(self):
        sessionId = self.headers.get('Session-ID')
        my_hid = session.getHashedUserid(sessionId)
        try:
            if not my_hid:
                raise AttributeError('unauthorized user')
            content_length = int(self.headers.get('Content-Length'))
            data = self.rfile.read(content_length).decode('utf-8').split('&')
            roomid = data[0]
            hids = data[1:]
            for hid in hids:
                if not user_repo_service.isExistHashedUserid(hid):
                    raise ValueError('user does not exist')
            chatRoom = chat_room_repo.getRoomByRoomid(roomid)
            chatRoom.addUsers(hids)
            self.send_response(201)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('201 success'.encode('utf-8'))
        except:
            self.send_response(400)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('400 failed'.encode('utf-8'))

    _get_control: dict = {
        '/users': _users,
        '/user/isoverlap': _isoverlap,
        '/user/me': _user_me,
        '/user/hashid': _get_user_hid,
        '/user/chat': _get_my_chatroom,
        '/chat/members/hashid': _get_members_huserid_in_room,
        '/chat/byroomid': _get_chatroom_by_roomid,
        '/chat/one-to-one': _do_chat_oneroom,
        '/friends': _get_friends_of_mine,
        '/info/byname': _find_by_name,
    }

    _post_control: dict = {
        '/user/join': _join,
        '/user/login': _login,
        '/user/patch': _patch,
        '/friends/add': _add_friend,
        '/chat/new': _create_chatting_room,
        '/chat/addMember': _add_chatting_member,
    }

    def do_GET(self):
        controller = self._get_control.get(self.path)
        if callable(controller):
            controller(self)

    def do_POST(self):
        controller = self._post_control.get(self.path)
        if callable(controller):
            controller(self)


def run_db_server():
    global db_server
    db_server = HTTPServer((IP, PORT), DbHTTPRequestHandler)
    print(f'DB server running on {IP}:{PORT}')
    db_server.serve_forever()
    # save after end
    user_repo_service.save_repository()
    chat_room_repo.save_as_file()


if __name__ == '__main__':
    run_db_server()
