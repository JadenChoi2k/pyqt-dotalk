import json_parser, json, datetime


class ChatDto:
    chatRoomId:str = None
    h_userid:str = None
    msg:str = None
    time:datetime.datetime = None

    def __init__(self, chatRoomId=None, h_userid=None, msg='', time=datetime.datetime.now()):
        self.chatRoomId = chatRoomId
        self.h_userid = h_userid
        self.msg = msg
        self.time = time

    def toJson(self):
        ret = {}
        ret['chatRoomId'] = self.chatRoomId
        ret['h_userid'] = self.h_userid
        ret['msg'] = self.msg
        ret['time'] = json_parser.time2str(self.time)
        return json.dumps(ret)

    def fromJson(data):
        try:
            json_data = json.loads(data)

            ret = ChatDto()
            ret.chatRoomId = json_data.get('chatRoomId')
            ret.h_userid = json_data.get('h_userid')
            ret.msg = json_data.get('msg')
            ret.time = json_parser.str2time(json_data.get('time'))
            return ret
        except Exception as e:
            print('ChatDto.fromJson has Exception: ', e)
            return None

    def __str__(self):
        return self.toJson()