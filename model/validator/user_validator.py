import datetime, re
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp


class UserValidator:

    """
    signup_date => validSignupDate (o)
    _signup_date => validSignupDate (o)
    signupdate => validSignupdate (x)
    """
    def validField(self, field, value):
        function_name = 'valid' + ''.join([word.capitalize() for word in field.split('_')])
        if hasattr(self, function_name):
            func = getattr(self, function_name)
            if callable(func):
                return func(self, value)
        return False

    def validUserid(self, userid):
        valid_rx = QRegExp('[A-z0-9]{4, 15}')
        if valid_rx.exactMatch(userid) is True:
            return userid
        else:
            return None

    def validPassword(self, password):
        if len(password) < 4 or len(password) > 20:
            return None
        invalid_rx = QRegExp('[ㄱ-ㅎㅏ-ㅣ가-힣 ]')
        if invalid_rx.indexIn(password) > -1:
            return None

        return password

    def validName(self, name):
        kor_rx = QRegExp('[가-힣]{2, 8}')
        eng_rx = QRegExp('[A-z]{2, 16}')
        if kor_rx.exactMatch(name) or eng_rx.exactMatch(name):
            return name
        else:
            return None

    def validOfficePhone(self, phone):
        phone_rx = re.complile(r'[\d]{3}-[\d]{4}')
        if re.search(phone_rx, phone):
            return phone
        return None

    def validEmail(self, email):
        email_rx = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        if re.search(email_rx, email):
            return email
        return None

    def validCellphone(self, phone):
        phone_rx = re.compile(r'[\d]{3}-[\d]{4}-[\d]{4}')
        if re.search(phone_rx, phone):
            return phone_rx
        return None

    def validDepartment(self, department):
        depart_rx = QRegExp('[가-힣0-9 ]{2, 12}')
        if depart_rx.exactMatch(department):
            return department
        return None

    def validPosition(self, position):
        position_rx = QRegExp('[가-힣 ]{2, 12}')
        if position_rx.exactMatch(position):
            return position
        return None

    def validBirth(self, date):
        now = datetime.date.today()
        days = now - date
        age = days.days // 365
        if 15 < age < 100:
            return date
        return None

    def validSignupDate(self, signupdate):
        now = datetime.datetime.now()
        elapsed = now - signupdate
        if elapsed.seconds < -1:
            return None
        if elapsed.seconds > 60 * 60:
            return None
        return signupdate

    def validComment(self, comment):
        if 0 < len(comment) <= 50:
            return comment
        return None

    def validColor(self, color:str):
        hex_rx = re.compile("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
        if re.search(hex_rx, color):
            return color
        return None