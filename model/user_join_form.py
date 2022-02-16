import datetime, json
from json_parser import date2str, str2date
from ui.ui_const import UIConst


class UserJoinForm:
    userid:str = None
    password:str = None
    name:str = None
    department:str = None
    position:str = None
    birth:datetime.date = None
    color:str = UIConst.SKYBLUE

    def __init__(self, userid, password, name, department, position, birth, color):
        self.userid = userid
        self.password = password
        self.name = name
        self.department = department
        self.position = position
        self.birth = birth
        self.color = color

    def toJson(self):
        dic = {
            'userid':self.userid,
            'password':self.password,
            'name':self.name,
            'department':self.department,
            'position':self.position,
            'birth':date2str(self.birth),
            'color':self.color
        }
        return json.dumps(dic)

    def fromJson(jstr:str):
        dic = json.loads(jstr)
        return UserJoinForm(
            dic.get('userid'),
            dic.get('password'),
            dic.get('name'),
            dic.get('department'),
            dic.get('position'),
            str2date(dic.get('birth')),
            dic.get('color')
        )
