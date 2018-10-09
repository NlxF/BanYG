"""custom forms"""
from flask_wtf import FlaskForm, RecaptchaField
from flask_user.forms import RegisterForm, LoginForm
from wtforms import StringField, SubmitField


class MyRegisterForm(RegisterForm):
    # recaptcha = RecaptchaField()
    pass


class MyLoginForm(LoginForm):
    # email = None
    pass


class UserProfileForm(FlaskForm):
    # first_name = StringField('First name', validators=[
    #     validators.DataRequired('First name is required')])
    # last_name = StringField('Last name', validators=[
    #     validators.DataRequired('Last name is required')])
    submit = SubmitField('Save')
