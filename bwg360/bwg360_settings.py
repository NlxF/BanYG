# -*- coding: utf-8 -*-
import os

# Application settings
APP_NAME                      = "BanYG360"
APP_SYSTEM_ERROR_SUBJECT_LINE = APP_NAME + " System Error:"

TEMPLATES_AUTO_RELOAD = True

# Flask CSRF settings
CSRF_ENABLED          = True

# Flask-DebugToolbar requires the 'SECRET_KEY' config
SECRET_KEY                   = "PASSWORD"
DEBUG_TB_INTERCEPT_REDIRECTS = False

# cache setting
# CACHE_TYPE = 'simple'
CACHE_TYPE                 = 'redis'
CACHE_KEY_PREFIX           = 'BanYG360'
CACHE_REDIS_HOST           = '127.0.0.1'
CACHE_REDIS_PORT           = 6379
CACHE_REDIS_DB             = 0
CACHE_REDIS_PASSWORD       = ""
CACHE_DEFAULT_TIMEOUT      = 60 * 15          # flask_cache  15分钟缓存失效
MYREDIS_DEFAULT_TIMEOUT    = 60 * 150         # MyRedisCache 150分钟缓存失效
CACHE_VISITOR_SEARCH_LIMIT = 60 * 5           # 设置搜索结果5分钟后超时

# SQLAlchemy settings
# SQLALCHEMY_DATABASE_URI = 'sqlite:///{}/test.db'.format(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
# SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://***:***@localhost/{}?charset=utf8'.format(APP_NAME)
SQLALCHEMY_NATIVE_UNICODE = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True
SQLALCHEMY_POOL_TIMEOUT = 30

# celery setting
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'db+mysql://***:***@localhost/{}'.format(APP_NAME)
CELERY_TASK_RESULT_EXPIRES = 120

# recaptcha settings
WTF_CSRF_ENABLED      = True

# Flask-Mail SMTP server settings
MAIL_DEBUG = True
MAIL_USERNAME       = '******@*****.com'
MAIL_PASSWORD       = '******'
MAIL_DEFAULT_SENDER = '"BYG360" <******@******.com>'
MAIL_SERVER         = '*********'
MAIL_PORT           = 587        #25
# MAIL_USE_SSL      = True       #465
MAIL_USE_TLS        = True       #587
MAIL_MAX_EMAILS = 500


# IP 地址查询URL, 服务端IP更改后需要修改http://lbsyun.baidu.com/apiconsole/key的白名单
URL_QUERY = 'http://api.map.baidu.com/location/ip?ak=**********&ip='


############################### Flask-User Features settings #####################################
USER_APP_NAME                      = "搬运工"
USER_ENABLE_USERNAME               = True         # Register and Login with username
USER_ENABLE_CHANGE_USERNAME        = True         # Allow users to change their username
USER_ENABLE_EMAIL                  = True         # Allow users to login and register with an email address
USER_ENABLE_CONFIRM_EMAIL          = True         # Force users to confirm their email
USER_ENABLE_CHANGE_PASSWORD        = True         # Allow users to change their password
USER_ENABLE_FORGOT_PASSWORD        = True         # Allow users to reset their passwords
USER_ENABLE_REGISTRATION           = False         # Allow new users to register
USER_ENABLE_LOGIN_WITHOUT_CONFIRM  = False        # Allow users to login without a confirmed email address Protect views using @confirm_email_required
USER_ENABLE_MULTIPLE_EMAILS        = False        # Users may register multiple emails Requires USER_ENABLE_EMAIL=True
USER_ENABLE_INVITATION             = False        # Allow users to invite Friends
USER_ENABLE_REMEMBER_ME            = True         # Remember user sessions across browser restarts.
USER_REQUIRE_RETYPE_PASSWORD       = True         # Prompt for `retype password` in:
USER_REQUIRE_INVITATION            = False        # Only invited users may register.
USER_CONFIRM_EMAIL_EXPIRATION      = 1*24*3600    # 1 days
USER_INVITE_EXPIRATION             = 7*24*3600    # 7 days
USER_RESET_PASSWORD_EXPIRATION     = 1*24*3600    # 1 days
DEFAULT_MAIL_SENDER                = 'BanYG'

#: Template file settings
USER_CHANGE_PASSWORD_TEMPLATE      = 'flask_user/change_password.html'
USER_CHANGE_USERNAME_TEMPLATE      = 'flask_user/change_username.html'
USER_EDIT_USER_PROFILE_TEMPLATE    = 'flask_user/edit_user_profile.html'
USER_FORGOT_PASSWORD_TEMPLATE      = 'flask_user/forgot_password.html'
USER_INVITE_USER_TEMPLATE          = 'flask_user/invite_user.html'
USER_LOGIN_TEMPLATE                = 'flask_user/login.html'
USER_LOGIN_AUTH0_TEMPLATE          = 'flask_user/login_auth0.html'
USER_MANAGE_EMAILS_TEMPLATE        = 'flask_user/manage_emails.html'
USER_REGISTER_TEMPLATE             = 'flask_user/register.html'
USER_RESEND_CONFIRM_EMAIL_TEMPLATE = 'flask_user/resend_confirm_email.html'

#: Email template file settings
USER_RESET_PASSWORD_TEMPLATE         = 'flask_user/reset_password.html'
USER_CONFIRM_EMAIL_TEMPLATE          = 'flask_user/emails/confirm_email'
USER_INVITE_USER_EMAIL_TEMPLATE      = 'flask_user/emails/invite_user'
USER_PASSWORD_CHANGED_EMAIL_TEMPLATE = 'flask_user/emails/password_changed'
USER_REGISTERED_EMAIL_TEMPLATE       = 'flask_user/emails/registered'
USER_RESET_PASSWORD_EMAIL_TEMPLATE   = 'flask_user/emails/reset_password'

#: RL settings
USER_CHANGE_PASSWORD_URL = '/user/change-password'
USER_CHANGE_USERNAME_URL = '/user/change-username'
USER_CONFIRM_EMAIL_URL = '/user/confirm-email/<token>'
USER_EDIT_USER_PROFILE_URL = '/user/edit_user_profile'
USER_EMAIL_ACTION_URL = '/user/email/<id>/<action>'
USER_FORGOT_PASSWORD_URL = '/user/forgot-password'
USER_INVITE_USER_URL = '/user/invite'
USER_LOGIN_URL = '/user/sign-in'
USER_LOGOUT_URL = '/user/sign-out'
USER_MANAGE_EMAILS_URL = '/user/manage-emails'
USER_REGISTER_URL = '/user/register'
USER_RESEND_EMAIL_CONFIRMATION_URL = '/user/resend-email-confirmation'
USER_RESET_PASSWORD_URL = '/user/reset-password/<token>'

USER_AFTER_LOGIN_ENDPOINT   = 'bwg360.home_page'
USER_AFTER_LOGOUT_ENDPOINT  = 'bwg360.home_page'
USER_AFTER_CONFIRM_ENDPOINT = 'bwg360.home_page'
