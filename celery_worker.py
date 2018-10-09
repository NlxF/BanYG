# coding:utf-8
from bwg360 import create_app, celery

# 运行 celery -A celery_worker:celery worker --loglevel=info

# 创建一个 Flask 实例
# 推入 Flask application context
# 第一个操作很简单，其实也是初始化了 celery 实例。
# 第二个操作看起来有些奇怪，实际上也很好理解。
# 如果用过 Flask 就应该知道 Flask 的 Application Context 和 Request Context.
# Flask 一个很重要的设计理念是：在一个 Python 进程里可以运行多个应用（application），
# 当存在多个 application 时可以通过 current_app 获取当前请求所对应的 application.
# current_app 绑定的是当前 request 的 application 的引用，在非 request-response 环境里，是没有 request context 的，
# 所以调用 current_app 就会抛出异常（RuntimeError: working outside of application context）。
# 创建一个 request context 没有必要，而且消耗资源，所以就引入了 application context.
# app.app_context().push() 会推入一个 application context，后续所有操作都会在这个环境里执行，直到进程退出。
# 因此，如果在 tasks 里用到了 current_app 或其它需要 application context 的东西，就一定需要这样做。

# windows系统下用 3.1.25版本

app = create_app()

app.app_context().push()
