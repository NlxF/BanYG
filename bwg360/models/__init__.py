# -*- coding: utf-8 -*-
from bwg360 import db
from bwg360.util import TimeConver


class MyDateTime(db.TypeDecorator):

    impl = db.DateTime

    # 往数据库里面存数据, UTC
    def process_bind_param(self, value, dialect):
        # value = timezone.localize(value)
        return value
        # return value.strftime('%Y-%m-%d %H:%M:%S')

    # 从数据库里面读数据
    def process_result_value(self, value, dialect):
        try:
            value = TimeConver.time_to_asia(value)  # pytz.utc.localize(value).astimezone(timezone)
            return value
            # return value.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return value


__all__ = ['MyDateTime', 'db']


