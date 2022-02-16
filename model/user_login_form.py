import json


class UserLoginForm:
    userid:str = None
    password:str = None

    def __init__(self, userid, password):
        self.userid = userid
        self.password = password

    def toJson(self):
        dic = {'userid':self.userid, 'password':self.password}
        return json.dumps(dic)

    def fromJson(jstr:str):
        dic = json.loads(jstr)
        return UserLoginForm(dic.get('userid'), dic.get('password'))
