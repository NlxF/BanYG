"""
    some help methods
"""
import os
import re
import random
import logging
import logging.handlers
from bwg360.util.translation_utils import gettext as _
from bwg360.flask_user import MyUserManager


def generate_flag(flag, uuid):
    return "%s:%s" % (flag, uuid)


def generate_prefix(prefix, url):
    return "%s:%s" % (prefix, url)


def generate_crc_number(number_len):
    numbers = [random.randint(0, 9) for x in range(number_len)]
    crc_bit = sum(numbers) % 10
    numbers.append(crc_bit)
    return ''.join(str(x) for x in numbers)


def is_number_crc(crc_number):

    try:
        to_str = str(crc_number)
    except TypeError:
        return False

    int_list = [int(x) for x in list(to_str)]
    if sum(int_list[:-1]) % 10 == int_list[-1]:
        return True
    else:
        return False


def is_http_https_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'   # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url) is not None  # True


def setup_login_user(app, db):
    from bwg360.models.user import User
    user_manager = MyUserManager(app, db, User, UserInvitationClass=None)
    endpoint = 'user.edit_user_profile'     # remove
    rules = app.url_map._rules_by_endpoint.get(endpoint, None)
    if rules:
        for rule in rules:
            app.url_map._rules.remove(rule)
        del app.url_map._rules_by_endpoint[endpoint]
        app.url_map._remap = True
        app.url_map.update()


site_list = ['youtube-dl']


def setup_list_support_site():
    from bwg360.controllers.dlFiles import list_custom_support_site

    global site_list
    site_list.extend(list_custom_support_site())


def setup_logger(app):
    log_file = os.path.join(app.root_path, 'logs', 'log')
    logger_handler = logging.handlers.TimedRotatingFileHandler(log_file, when="midnight", encoding='utf-8')
    fmt_str = '[%(asctime)s]-[Process:%(process)d-Thread:%(thread)d]-[%(levelname)s]-[%(module)s.%(funcName)s:%(lineno)d]-[%(message)s]'
    fmt = logging.Formatter(fmt_str)
    logger_handler.setFormatter(fmt)
    logger_handler.setLevel(logging.INFO)

    app.logger.addHandler(logger_handler)

    # from logging.config import dictConfig
    # dictConfig({
    #     'version': 1,
    #     'formatters': {
    #         'default1': {
    #             'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    #         },
    #         'default2': {
    #             'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    #         },
    #     },
    #     'handlers': {
    #         'handler1': {
    #             'class': 'logging.StreamHandler',
    #             'stream': 'ext://flask.logging.wsgi_errors_stream',
    #             'formatter': 'default'
    #         },
    #         'handler2': {
    #             'class': 'logging.StreamHandler',
    #             'formatter': 'default'
    #         },
    #         'handler3': {
    #
    #         },
    #     },
    #     'root': {
    #         'level': 'INFO',
    #         'handlers': ['wsgi']
    #     }
    # })


def is_free_download(user):
    if not user:
        return True

    return user.is_anonymous or user.brick <= 0


_DOWNLOAD_FREE   = 512 * 1024         # 免费用户下载速度 512k
_DOWNLOAD_USER   = 1 * 1024 * 1024    # 注册用户下载速度 1M
_DOWNLOAD_MEMBER = 2 * 1024 * 1024    # 会员用户下载速度 2M


def get_download_speed(user):
    # Download rate

    if not user:
        return _DOWNLOAD_FREE

    if is_free_download(user):
        return _DOWNLOAD_USER

    return _DOWNLOAD_MEMBER


def file_size(filename):
    try:
        statinfo = os.stat(filename)
        return statinfo.st_size
    except Exception as e:
        return 0


def update_cookies(ydl_opts):
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    cookie_path = os.path.join(base_path, "cookies.txt")
    # print(cookie_path)
    ydl_opts['cookiefile'] = cookie_path


def adblock_plus_path():
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    adblock_path = os.path.join(base_path, "Adblock-Plus_v1.13.2.crx")
    return adblock_path


def error_message_filter(err_msg):
    if "Unable to download JSON metadata" in err_msg:
        return _('Unable to download JSON metadata!')
    elif "timed out" in err_msg:
        return _("request timed out!")
    elif "Connection refused" in err_msg:
        return _("Connection refused!")
    elif "error -6004:" in err_msg:
        return _("客户端无权播放")
    elif "10054" in err_msg:
        return _("远程主机强迫关闭了一个现有的连接")
    elif "Unable to extract title" in err_msg:
        return _("The video does not exist!")

    return err_msg  # _('Unknown error, please try again later!')
