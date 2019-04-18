from sqlalchemy import literal, desc
from sqlalchemy.orm import synonym
from bwg360.util import Singleton
from bwg360.models import db
from bwg360.models import MyDateTime


class Notice(db.Model):
    __tablename__ = 'notices'

    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.Unicode(256))
    valid = db.Column('is_valid', db.Boolean, nullable=False, default=literal(True))
    created_time = db.Column(MyDateTime(), default=db.func.now())

    setting_id = db.Column(db.Integer(), db.ForeignKey('setting.id'))

    def is_valid(self):
        return self.valid

    def __repr__(self):
        return "<UserIP: {0}>".format(self.address)


class Setting(db.Model):
    """setting 表"""
    __tablename__ = 'setting'

    id = db.Column(db.Integer, primary_key=True)

    free_download_max_once = db.Column(db.Integer)
    free_download_one_day  = db.Column(db.Integer)
    _free_download_step_   = db.Column(db.String(128))
    free_download_search_limit   = db.Column(db.Integer)
    charge_download_search_limit = db.Column(db.Integer)

    free_download_speed = db.Column(db.Integer)
    user_download_speed = db.Column(db.Integer)
    memb_download_speed = db.Column(db.Integer)

    # Notices
    notices = db.relationship('Notice', order_by=desc(Notice.id), backref="setting", lazy='dynamic')

    @property
    def free_download_step(self):
        step = []
        for s in self._free_download_step_.split(','):
            try:
                step.append(int(s))
            except ValueError as exc:
                pass
        return tuple(step)

    @free_download_step.setter
    def free_download_step(self, value):
        if isinstance(value, list) or isinstance(value, tuple):
            step = ','.join(str(x) for x in value)
            self._free_download_step_ = step

    free_download_step = synonym('_free_download_step_', descriptor=free_download_step)

    def __repr__(self):
        return '<Setting :{}>'.format(self.id)


def init_site_settings():
    """init dynamic setting"""

    st = Setting.query.first()
    if not st:
        st = Setting(free_download_max_once=500,             # MB为单位
                     free_download_one_day=10*1024,          # MB为单位
                     free_download_step=(0, 5, 10, 20, 40),  # 连续下载间隔大于5分钟，10分钟，20分钟, 40分钟, 40分钟, 40分钟...,
                     free_download_search_limit=5*60,        # 游客下载设置搜索结果 5分钟后超时
                     charge_download_search_limit=10*60,     # 注册下载设置搜索结果10分钟后超时
                     free_download_speed=512*1024,           # 免费用户下载速度 512k
                     user_download_speed=1 * 1024 * 1024,    # 注册用户下载速度 1M
                     memb_download_speed=2 * 1024 * 1024)    # 会员用户下载速度 2M

    return st
