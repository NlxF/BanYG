from functools import wraps
from flask import session, request, flash, abort
from flask_user import current_user
from bwg360.util.translation_utils import custom_render_template
from bwg360.util.mycache import check_anonymous, check_free_user
from bwg360.forms.searchForm import SearchForm


def download_check(func):
    """
        游客下载校验：每天游客之能下载一次，
        免费下载校验：连续下载间隔大于5分钟，10分钟，20分钟, 40分钟....
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):

        if current_user.is_anonymous:
            # 游客下载限制
            msg = check_anonymous(session.get('fppkcookie'), request.remote_addr)
            if msg:
                flash(msg, 'error')
                return custom_render_template("page_home.html", form=SearchForm())
        elif current_user.brick <= 0:
            # 免费下载检查
            num, msg = check_free_user(current_user.username)
            if num > 0:
                flash(msg, 'error')
                return custom_render_template("page_home.html", form=SearchForm())

        # Call the actual view
        return func(*args, **kwargs)
    return decorated_view


def permission_check(func):
    """
        访问权限检查
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):

        if current_user.is_anonymous:
            abort(404)

        elif not current_user.roles or not current_user.roles[0].is_administrator:
            abort(404)

        # Call the actual view
        return func(*args, **kwargs)

    return decorated_view
