# -*- coding: utf-8 -*-
from sqlalchemy import literal, desc
from flask_user import UserMixin
from bwg360 import db
from bwg360.models import MyDateTime


# 登录IP表
class UserIp(db.Model):
    __tablename__ = 'user_ip'

    id = db.Column(db.Integer(), primary_key=True)
    login_time = db.Column(MyDateTime(), default=db.func.now(), onupdate=db.func.now())
    province = db.Column(db.Unicode(256))
    city = db.Column(db.Unicode(250))
    district = db.Column(db.Unicode(256))
    street = db.Column(db.Unicode(256))
    address = db.Column(db.String(255), default='')

    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))

    def __repr__(self):
        return "<UserIP: {0}>".format(self.address)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information. The collation='NOCASE' is required to search case insensitively
    # when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(db.String(100), nullable=False, unique=True)              # , collation='NOCASE'
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, default='')

    # User Email information
    email = db.Column(db.String(255), nullable=False, default=u'', unique=True)    # , collation='NOCASE'
    email_confirmed_at = db.Column(MyDateTime)

    # User information
    active = db.Column('is_active', db.Boolean, nullable=False, default=literal(False))
    # 砖头，1砖 = 1G, MB表示
    brick = db.Column('brick', db.Integer, nullable=False, default=literal(1024))
    vip_expire_at = db.Column(MyDateTime, nullable=True)     # TODO  add vip

    # user login information
    ips = db.relationship('UserIp', order_by=desc(UserIp.login_time), backref="user", lazy='dynamic')

    # Relationships
    roles = db.relationship('Role', secondary='users_roles', backref=db.backref('users', lazy='dynamic'))

    def is_active(self):
        return self.active

    @property
    def last_login(self):
        ip = self.ips.all().first()
        return ip.login_time if ip else u'未知'

    def __repr__(self):
        return "It's <{}>".format(self.username if self.is_authenticated else "anonymous")


# Define the Role data model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)  # for @roles_accepted()
    label = db.Column(db.Unicode(255), server_default=u'')  # for display purposes

    @property
    def is_administrator(self):
        return self.name == 'admin'

    def __repr__(self):
        return "Role's <{}>".format(self.label)


# Define the UserRoles association model
class UsersRoles(db.Model):
    __tablename__ = 'users_roles'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


class UserInvitation(db.Model):
    """招募

     Attributes:
         token-标记
         recruiter-招募者
         recruited-被招募者
    """
    __tablename__ = 'recruit'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.Unicode(40), nullable=False, default=u'')
    # recruiter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    # recruited_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
