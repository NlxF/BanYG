from flask import current_app
from flask_script import Command
from bwg360 import db
from bwg360.util import TimeConver
from bwg360.models.download import DownloadRecord, DBTag
from bwg360.models.tasks import TaskResult


class InitDbCommand(Command):
    """ Initialize the database."""

    def run(self):
        init_db()
        print('Database has been initialized.')


def init_db():
    """ Initialize the database."""
    db.drop_all()

    # dynamic create sharding table class
    download_record_class = DownloadRecord.model()

    db.create_all()

    create_users()


def create_users():
    """ Create users """

    # Adding roles
    admin_role  = find_or_create_role('admin', u'Admin')
    member_role = find_or_create_role('member', u'Member')

    # Add users
    user = find_or_create_user(u'***',  u'********',  '*******', admin_role)
    user = find_or_create_user(u'***',  u'********',  '*******', member_role)

    # add db tag
    init_db_tag()

    # Save to DB
    db.session.commit()


def find_or_create_role(name, label):
    """ Find existing role or create new role """
    from bwg360.models.user import Role
    role = Role.query.filter(Role.name == name).first()
    if not role:
        role = Role(name=name, label=label)
        db.session.add(role)
    return role


def find_or_create_user(username, email, password, role=None):
    """ Find existing user or create new user """
    from bwg360.models.user import User
    user = User.query.filter(User.email == email).first()
    if not user:
        user = User(email=email,
                    username=username,
                    password=current_app.user_manager.password_manager.hash_password(password),
                    active=True,
                    email_confirmed_at=TimeConver.utc_time_now())
        if role:
            user.roles.append(role)
        db.session.add(user)
    return user


def init_db_tag():
    """init db start tag"""

    start_tag = str(TimeConver.utc_time_now().strftime("%Y%m"))
    tag = DBTag.query.filter(DBTag.tag == start_tag).first()
    if not tag:
        tag = DBTag(tag=start_tag)
        db.session.add(tag)


