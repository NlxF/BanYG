"""custom user manager for customize properties"""
from flask_user import UserManager
from bwg360.flask_user.my_forms import MyRegisterForm, MyLoginForm


class MyUserManager(UserManager):

    def customize(self, app):
        # Add custom properties here
        self.RegisterFormClass = MyRegisterForm
        self.LoginFormClass = MyLoginForm