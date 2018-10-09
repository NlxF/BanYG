# coding: utf-8
from sqlalchemy import literal
from bwg360 import db


class TaskResult(db.Model):
    __tablename__ = 'task_result'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(50), nullable=False, unique=True)
    task_name = db.Column(db.String(50), nullable=False)
    create_time = db.Column(db.DateTime, default=db.func.now())
    args = db.Column(db.Unicode(256), nullable=True)
    kwargs = db.Column(db.Unicode(256), nullable=True)
    err_code = db.Column(db.String(50))
    exc_msg = db.Column(db.String(256))
    status = db.Column(db.Boolean, nullable=False, default=literal(False))

    def __repr__(self):
        return "<task {0}, result: {1}>".format(self.task_name, self.status)


