from model.validator.user_validator import UserValidator
from model.user_join_form import UserJoinForm


class UserJoinFormValidator:
    _validator = UserValidator()

    # returns (result, error code)
    def valid(self, form:UserJoinForm)->tuple:
        try:
            if type(form) is not UserJoinForm: return False, 'type-error'
            _validator = UserJoinFormValidator._validator
            if not _validator.validUserid(form.userid): return False, 'wrong-userid'
            if not _validator.validPassword(form.password): return False, 'wrong-password'
            if not _validator.validName(form.name): return False, 'wrong-name'
            if not _validator.validDepartment(form.department): return False, 'wrong-department'
            if not _validator.validPosition(form.position): return False, 'wrong-position'
            if not _validator.validBirth(form.birth): return False, 'wrong-birth'
            if not _validator.validSingupDate(form.singup_date): return False, 'wrong-signupdate'
            if not _validator.validColor(form.color): return False, 'wrong-color'
            return True, 'ok'
        except Exception as e:
            return False, str(e)