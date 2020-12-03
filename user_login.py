from flask_login import UserMixin


class User(UserMixin):

    def __init__(self,id,user_pwd,user_name,user_type,org_id,org_name,org_notice) -> None:
        self.id = id
        self.user_pwd = user_pwd
        self.user_name = user_name.title()
        self.user_type = user_type.title()
        self.org_id = org_id
        self.org_name = org_name.title()
        self.org_notice = org_notice.title()

    def is_authenticated(self,passwd):
        if str(self.user_pwd) == str(passwd):
            return True
        else:
            return False

    def is_authenticated_admin(self,type):
        if str(type) == str('Manager'):
            return True
        else:
            return False
        
