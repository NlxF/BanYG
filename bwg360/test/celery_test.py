# coding: utf-8

import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import unittest
from flask import session
from celery_worker import app
from bwg360.tasks import jobs
from bwg360.models.user import User
from flask_user.user_manager__views import login_user


# def login():
#     user = User.query.filter(User.username == 'luffy').first()
#     if login_user(user):
#         print("login successful.")
#         return user
#
#
# def test_task():
#     user = login()
#     tasks.send_registered_email.delay(user, None, require_email_confirmation=True)
#
#
# if __name__ == '__main__':
#     # app.run(debug=True)
#     with app.app_context():
#         # within this block, current_app points to app.
#         test_task()


class FlaskCeleryTaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        self.app_context.pop()

    def login(self):
        user = User.query.filter(User.username=='luffy').first()
        if login_user(user):
            print("login successful.")
            return user

    def test_task(self):
        with app.test_client() as client:
        # with app.app_context():
        #     response = client.post('/foo', data=dict(), follow_redirects=True)
        #     print('session is:', session)
            # user = self.login()
            user = User.query.filter(User.username == 'Member').first()
            jobs.query_ip.delay(user, '**.**.**.**')


if __name__ == "__main__":
    unittest.main()
