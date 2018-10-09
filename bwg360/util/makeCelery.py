# coding: utf-8
from celery import Celery


def make_celery(app):
    celery = Celery(app.import_name, broker='redis://localhost:6379/0')  # , include=['wuaiwow.socketConnect']
    # celery.conf.update(
    #     CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND,
    #     CELERY_TASK_RESULT_EXPIRES=CELERY_TASK_RESULT_EXPIRES
    # )

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
