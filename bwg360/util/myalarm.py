"""
    Used for timing tasks
"""
from bwg360.util import TimeConver
from bwg360.util.mycache import set_free_download_size, get_init_free_download_size
try:
    from uwsgidecorators import cron, timer
except ImportError:
    def cron(*args):
        def decorator(func):
            def wrapper(*args):
                func()
            return wrapper
        return decorator

    def timer(*args):
        def decorator(func):
            def wrapper(*args):
                func()
            return wrapper
        return decorator


def _set_free_download():
    def _find_or_create_record(tag):
        from bwg360.models.download import FreeDownloadINFO, db

        fd = FreeDownloadINFO.query.filter_by(tag=tag).first()
        if not fd:
            fd = FreeDownloadINFO(start=get_init_free_download_size())
            db.session.add(fd)
            db.session.commit()

        return fd

    _tag = str(TimeConver.utc_time_now().date())
    _fd = _find_or_create_record(_tag)

    set_free_download_size(_fd.end)


@cron(40, 4, -1, -1, -1)    # min, hour, day, mon, wday, func
# @timer(30)
def reset_free_download(signum):
    # print("it's 4:40 in the morning: reset free download!")
    print("130 seconds elapsed")

    _set_free_download()


@cron(30, 3, 28, -1, -1)    # 每个月的28号3:30生成新的下载记录表
# @timer(30)
def create_download_record_table(signum):
    from bwg360.models.download import DownloadRecord, db
    latest_record = DownloadRecord.model()
    next_tag = DownloadRecord.next_tag(latest_record.model_tag)
    print('next tag is:', next_tag)
    if next_tag is not None:
        next_record = DownloadRecord.model(next_tag)

        db.create_all()


def init_free_download():
    """when server start, initialize the free download"""

    _set_free_download()



# import uwsgi
# import signal
# import datetime
# from . import Singleton
#
#
# class MyAlarm(metaclass=Singleton):
#     def __init__(self, alarm_type, start, interval):
#         self.alarm_type = alarm_type
#         self.interval = interval
#         self.clicking = False
#         self.start = start
#
#     def start_alarm(self, handler):
#         if self.alarm_type == signal.ITIMER_REAL:
#             register_type = signal.SIGALRM
#         elif self.alarm_type == signal.ITIMER_VIRTUAL:
#             register_type = signal.SIGVTALRM
#         else:
#             register_type = signal.SIGPROF
#
#         if self.clicking:
#             return
#
#         try:
#             self.clicking = True
#             signal.signal(register_type, handler)
#             signal.setitimer(self.alarm_type, self.start, self.interval)
#             print("start alarm:{}".format(self))
#         except signal.ItimerError as e:
#             self.clicking = False
#             RuntimeError("Init alarm error:{}".format(e))
#
#     def stop_alarm(self):
#         signal.setitimer(self.alarm_type, 0, 0)
#         self.clicking = False
#
#
# def setup_alarm():
#     def handler(signum, frame):
#         print('Signal handler called with signal:{}----{}'.format(signum, frame))
#
#     now = datetime.datetime.now()
#     seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
#     day_seconds = 86400
#     # alarm = MyAlarm(signal.ITIMER_REAL, day_seconds-seconds_since_midnight, day_seconds)
#     alarm = MyAlarm(signal.ITIMER_REAL, 5, 5)
#     alarm.start_alarm(handler)
