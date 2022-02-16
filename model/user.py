import datetime, json
from json_parser import date2str, str2date, time2str, str2time
from util import utils


class User:
    _id:int = None
    _userid:str = None
    _password:str = None
    _name:str = None
    _office_phone:str = None
    _email:str = None
    _cellphone:str = None
    _department:str = None
    _position:str = None
    _birth:datetime.date = None
    _signup_date:datetime.date = None
    _comment:str = None
    _color:str = None

    def __init__(self, userid=None, password=None, name=None, office_phone=None, email=None, cellphone=None,
                 department=None, position=None, birth=None, signup_date=None, comment=None, color="#92B5D9"):
        self._userid = userid
        self._password = password
        self._name = name
        self.office_phone = office_phone
        self._email = email
        self._cellphone = cellphone
        self._department = department
        self._position = position
        self._birth = birth
        self._signup_date = signup_date
        self._comment = comment
        self._color = color

    def get_id(self):
        return self._id

    def set_id(self, new_id:int):
        self._id = new_id

    def get_userid(self):
        return self._userid

    def set_userid(self, new_id:str):
        self._userid = new_id

    def get_hashed_userid(self):
        if hasattr(self, 'hid'):
            return self.hid
        userid = self.get_userid()
        if not userid:
            return userid
        self.hid = str(utils.hashDigest(userid))
        return self.hid

    def get_password(self):
        return self._password

    def set_password(self, new_password):
        self._password = new_password

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_office_phone(self):
        return self._office_phone

    def set_office_phone(self, phone):
        self._office_phone = phone

    def get_email(self):
        return self._email

    def set_email(self, email):
        self._email = email

    def get_cellphone(self):
        return self._cellphone

    def set_cellphone(self, phone):
        self._cellphone = phone

    def get_department(self):
        return self._department

    def set_department(self, depart):
        self._department = depart

    def get_position(self):
        return self._position

    def set_position(self, pos):
        self._position = pos

    def get_birth(self):
        return self._birth

    def set_birth(self, date):
        if self.get_birth() is not None:
            return None
        self._birth = date

    def get_signup_date(self):
        return self._sginup_date

    def set_signup_date(self, datetime):
        if self.get_signup_date() is not None:
            return None

        self._signup_date = datetime

    def get_comment(self):
        return self._comment

    def set_comment(self, comment):
        self._comment = comment

    def get_color(self):
        return self._color

    def set_color(self, color:str):
        self._color = color

    def from_list(item_list:list):
        return User(*item_list)

    def to_list(self):
        return [
            self._id,
            self._userid,
            self._password,
            self._name,
            self._office_phone,
            self._email,
            self._cellphone,
            self._department,
            self._position,
            self._birth,
            self._signup_date,
            self._comment,
            self._color,
        ]

    def toJson(self):
        dic = {
            'userid':self._userid,
            'password':'self._password',
            'name':self._name,
            'office_phone':self._office_phone,
            'email':self._email,
            'cellphone':self._cellphone,
            'department':self._department,
            'position':self._position,
            'birth':date2str(self._birth),
            'signup_date':time2str(self._signup_date),
            'comment':self._comment,
            'color':self._color
        }
        return json.dumps(dic)

    def fromJson(jstr:str):
        dic = json.loads(jstr)
        return User(
            dic.get('userid'),
            dic.get('password'),
            dic.get('name'),
            dic.get('office_phone'),
            dic.get('email'),
            dic.get('cellphone'),
            dic.get('department'),
            dic.get('position'),
            str2date(dic.get('birth')),
            str2time(dic.get('signup_date')),
            dic.get('comment'),
            dic.get('color')
        )

    def toJsonFull(self):
        dic = {
            'userid': self._userid,
            'password': self._password,
            'name': self._name,
            'office_phone': self._office_phone,
            'email': self._email,
            'cellphone': self._cellphone,
            'department': self._department,
            'position': self._position,
            'birth': date2str(self._birth),
            'signup_date': time2str(self._signup_date),
            'comment': self._comment,
            'color': self._color
        }
        return json.dumps(dic)

    def fromJson(jstr:str):
        dic = json.loads(jstr)
        return User(
            dic.get('userid'),
            dic.get('password'),
            dic.get('name'),
            dic.get('office_phone'),
            dic.get('email'),
            dic.get('cellphone'),
            dic.get('department'),
            dic.get('position'),
            str2date(dic.get('birth')),
            str2time(dic.get('signup_date')),
            dic.get('comment'),
            dic.get('color')
        )
        user.set_id(dic.get('id'))
        return user

    def __str__(self):
        return self.toJson()