from sqlalchemy import literal
from bwg360.util import TimeConver
from bwg360.models import db, MyDateTime


class DBTag(db.Model):
    __tablename__ = 'db_start_tag'

    _start_tag = None

    id  = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(256))

    @staticmethod
    def start_tag():
        if DBTag._start_tag is None:
            DBTag._start_tag = DBTag.query.limit(1).first().tag

        return DBTag._start_tag

    def __repr__(self):
        return '<db start tag:{}>'.format(self.tag)


class DownloadRecord(object):
    """下载记录分表"""
    _mapper = {}

    @staticmethod
    def model(tag=None):
        if tag is None:
            tag = str(TimeConver.utc_time_now().strftime("%Y%m"))
        class_name = 'DownloadRecord_{}'.format(tag)

        ModelClass = DownloadRecord._mapper.get(class_name, None)
        if ModelClass is None:
            ModelClass = type(class_name, (db.Model,), {
                '__module__'   : __name__,
                '__name__'     : class_name,
                '__tablename__': 'downloads_record_{}'.format(tag),
                'model_tag': tag,
                'id'   : db.Column(db.Integer, primary_key=True),
                'url'  : db.Column(db.Unicode(1024)),
                'title': db.Column(db.Unicode(1024)),
                'ip'   : db.Column(db.String(64)),
                'fp'   : db.Column(db.String(62)),
                'username'   : db.Column(db.String(80), nullable=True),
                'user_id'    : db.Column(db.Integer, nullable=True),
                'time'       : db.Column(MyDateTime, default=db.func.now()),
                'is_free'    : db.Column("is_free", db.Boolean, default=literal(0)),
                'is_complete': db.Column("complete", db.Boolean, default=literal(1)),
                'size'       : db.Column("download_size", db.Float, default=literal(100)),
            })
            DownloadRecord._mapper[class_name] = ModelClass

        cls = ModelClass
        return cls

    @staticmethod
    def previous_tag(tag=None):
        if tag is None or len(tag) <= 0:
            return None
        start_tag   = DBTag.start_tag()
        start_year  = int(start_tag[:-2])
        start_month = int(start_tag[-2:])
        tag_year  = int(tag[:-2])
        tag_month = int(tag[-2:])
        if tag_year < start_year or (tag_year == start_year and tag_month <= start_month):
            return None

        if tag_month == 1:
            return "{:4d}{:02d}".format(tag_year - 1, 12)
        else:
            return "{:4d}{:02d}".format(tag_year, tag_month - 1)

    @staticmethod
    def next_tag(tag=None):
        if tag is None or len(tag) <= 0:
            return None
        start_tag   = DBTag.start_tag()
        start_year  = int(start_tag[:-2])
        start_month = int(start_tag[-2:])
        tag_year  = int(tag[:-2])
        tag_month = int(tag[-2:])
        if tag_year < start_year or (tag_year == start_year and tag_month < start_month):
            return None

        if tag_month == 12:
            return "{:4d}{:02d}".format(tag_year + 1, 1)
        else:
            return "{:4d}{:02d}".format(tag_year, tag_month + 1)


class FreeDownloadINFO(db.Model):
    """记录免费下载的信息"""
    __tablename__ = 'free_download_count'

    id    = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Integer, nullable=False)   # default=literal(100)
    end   = db.Column(db.Integer, nullable=False)
    tag   = db.Column(db.String(20))
    time_start = db.Column(MyDateTime, default=db.func.now())
    time_end   = db.Column(MyDateTime, default=db.func.now(), onupdate=db.func.now())

    def __init__(self, start, end=None):
        self.start = start
        if end is None:
            end = start
        self.end = end
        self.tag = str(TimeConver.utc_time_now().date())

    def __repr__(self):
        return '<FreeDownloadINFO start at:{} with size:{},end at:{}>'.format(self.time_start, self.start, self.time_end)


class DownloadStatus(object):
    """used for notify download status"""
    def __init__(self):
        self.url   = ""
        self.title = ""

        self.status   = 0              # 下载状态，0：未下载; 1: 正在下载; 2: 下载完成; 3: 下载出错
        self.filename = ""             # 片段名或临时文件名
        self.total_size   = 0          # 下载总量（字节）
        self.current_size = 0          # 当前下载量（字节）
        self.fragment_index = -1       # 下载的片段索引

        self.start_position = 0        # 临时文件读取开始地址
        self.length = 0                # 临时文件读取长度
