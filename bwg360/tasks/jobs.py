# coding: utf-8
import json
from flask import current_app
from bwg360 import celery, db, celery_logger
from bwg360.models.user import UserIp, User
from bwg360.models.tasks import TaskResult
from urllib.request import urlopen


def retry_delay(ts):
    """
        返回下次重发的时间间隔, 间隔为15s, 单位:秒
    """
    return 15 * ts


class JobTask(celery.Task):
    """
        继承的Task类,用来定义成功或者失败时的动作
    """

    def on_success(self, retval, task_id, args, kwargs):
        task = TaskResult.query.filter(TaskResult.task_id == task_id).first()
        if task:
            task.status = True
        else:
            task = TaskResult(task_id=task_id,
                              task_name=self.name,
                              args=json.dumps(args),
                              kwargs=json.dumps(kwargs),
                              err_code=-110,
                              exc_msg='')
        db.session.add(task)
        db.session.commit()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if isinstance(exc, Exception):
            errno = exc.errno if hasattr(exc, 'errno') else -110
            message = exc.message if hasattr(exc, 'message') else 'Unknow error'
            task = TaskResult(task_id=task_id,
                              task_name=self.name,
                              args=json.dumps(args),
                              kwargs=json.dumps(kwargs),
                              err_code=errno,
                              exc_msg=message)
            db.session.add(task)
            db.session.commit()


@celery.task(base=JobTask, bind=True)       # max_retries 为尝试的次数，不包括首次
def query_ip(self, user_id, ip_address):
    """
        查询ip详情
    """
    user = User.query.filter(User.id == user_id).first()
    ips = UserIp.query.filter_by(user=user).order_by(UserIp.login_time).all()
    ip = ips[0] if len(ips) == 30 else UserIp()
    ip.user = user
    ip.address = ip_address
    try:
        url = "%s%s" % (current_app.config['URL_QUERY'], ip.address)
        resp = urlopen(url, timeout=5)
        address_json = resp.read()
        address_dict = json.loads(address_json)
        if address_dict['status'] == 0:
            content = address_dict.get('content', None)
            address_detail = content.get('address_detail', None)
            if address_detail:
                ip.province = address_detail['province'] if len(address_detail['province']) else u'未知'
                ip.city = address_detail['city'] if len(address_detail['city']) else u'未知'
                ip.district = address_detail['district'] if len(address_detail['district']) else u'未知'
                ip.street = address_detail['street'] if len(address_detail['street']) else u'未知'
    except Exception as exc:
        ip.province = ip.city = ip.district = ip.street = u'未知'
        # raise self.retry(exc=exc, countdown=retry_delay(self.request.retries))

    user.ips.append(ip)

    db.session.add(user)
    db.session.add(ip)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()

