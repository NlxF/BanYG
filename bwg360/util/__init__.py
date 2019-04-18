# -*- coding: utf-8 -*-
import sys
import pytz
from sys import platform
from datetime import datetime
# from flask_babelex import gettext as _
from bwg360.util.translation_utils import gettext as _

if platform == "linux" or platform == "linux2":
    platform_ = 1  # linux
elif platform == "darwin":
    platform_ = 2  # OS X
elif platform == "win32":
    platform_ = 3  # Windows...

PY2 = sys.version_info[0] == 2

if PY2:
    unichr = unichr
    text_type = unicode
    string_types = (str, unicode)
    integer_types = (int, long)
else:
    unichr = chr
    text_type = str
    string_types = (str, )
    integer_types = (int, )


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TimeConver(object):
    timezone = pytz.timezone("Asia/Shanghai")

    @classmethod
    def utc_time_now(cls):
        return datetime.utcnow()

    @classmethod
    def asia_time_now(cls):
        utc_now = TimeConver.utc_time_now()
        return pytz.utc.localize(utc_now).astimezone(cls.timezone)

    @classmethod
    def time_to_asia(cls, value):
        if not isinstance(value, datetime):
            raise Exception("Parameter type error, need datetime type")

        return pytz.utc.localize(value).astimezone(cls.timezone)


# redis keys
free_download_max_once         = 500
free_download_one_day          = 10 * 1024           # MB为单位
search_flag                    = "SearchFlag"
search_prefix                  = "SearchURL"
free_download_prefix           = "FreeDownload"
size_free_download             = "{}:Size".format(free_download_prefix)
anonymous_free_download        = "{}:anonymous".format(free_download_prefix)
sequence_free_download_prefix  = "{}:Sequence".format(free_download_prefix)
sequence_free_download_step    = [0, 5, 10, 20, 40]    # 连续下载间隔大于5分钟，10分钟，20分钟, 40分钟, 40分钟, 40分钟...
sequence_free_download_toast   = [_('Congratulations, you can do it.'),                 # 恭喜你，可以下载
                                 _('You have downloaded, try again after {} minutes'),     # 你已经下载过了, 分钟后再尝试
                                 _('Leave some for others, try again after {} minutes'),   # 留点给别人吧, 分钟后再尝试
                                 _('Free traffic is running out, try again after {} minutes'),  # 免费流量快用完了，分钟后再尝试
                                 _('Run out of traffic, try again after {} minutes')]      # 流量快用完了，分钟后再尝试
over_total_free_download_toast = _("Free download traffic is over")                        # 免费下载流量用完了
visitor_no_free_download_toast = _('visitor can only download once a day for free')


__all__ = ['filters', 'TimeConver', 'string_types', 'search_flag', 'search_prefix', 'free_download_max_once',
           'Singleton']
