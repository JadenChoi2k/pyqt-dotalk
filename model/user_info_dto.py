from model.user import User
from datetime import date
import hashlib, json
import json_parser


class UserInfoDto:
    h_userid:str = None
    name:str = None
    office_phone:str = None
    email:str = None
    department:str = None
    position:str = None
    birth:date = None
    comment:str = None
    color:str = None

    def fromUser(user:User):
        m = hashlib.sha256()
        m.update(user.get_userid().encode('utf-8'))
        h_userid = str(m.digest())

        result = UserInfoDto()
        result.h_userid = h_userid
        result.name = user.get_name()
        result.office_phone = user.get_office_phone()
        result.email = user.get_email()
        result.department = user.get_department()
        result.position = user.get_position()
        result.birth = user.get_birth()
        result.comment = user.get_comment()
        result.color = user.get_color()

        return result

    def toJson(self):
        dic = {}
        dic['h_userid'] = self.h_userid
        dic['name'] = self.name
        dic['office_phone'] = self.office_phone
        dic['email'] = self.email
        dic['department'] = self.department
        dic['position'] = self.position
        dic['birth'] = json_parser.date2str(self.birth)
        dic['comment'] = self.comment
        dic['color'] = self.color

    def fromJson(jstr:str):
        dic = json.loads(jstr)

        ret = UserInfoDto()
        ret.h_userid = dic.get('h_userid')
        ret.name = dic.get('name')
        ret.office_phone = dic.get('office_phone')
        ret.email = dic.get('email')
        ret.department = dic.get('department')
        ret.position = dic.get('position')
        ret.birth = json_parser.str2date(dic.get('birth'))
        ret.comment = dic.get('comment')
        ret.color = dic.get('color')

        return ret
