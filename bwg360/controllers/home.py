# -*- coding: utf-8 -*-
import uuid
import gevent
from flask import (Blueprint, flash, Response,
                   redirect, request, url_for, make_response, g)
from flask_user import current_user, login_required
from flask_user.signals import user_logged_in, user_logged_out
from bwg360 import db, app
from bwg360.models.download import DownloadRecord
from bwg360.forms.searchForm import SearchForm, DetailForm, FormatsForm
from bwg360.controllers.dlFiles import make_file_dl
from bwg360.util.translation_utils import custom_render_template, gettext as _
from bwg360.util.plugHelper import add_blueprint
from bwg360.util import string_types, search_flag, search_prefix, free_download_max_once
from bwg360.util.decorators import download_check
from bwg360.util.utils import (error_message_filter, generate_crc_number, is_free_download, site_list,
                               generate_flag, generate_prefix)
from bwg360.util.mycache import MyRedisCache, get_file_size_of_format_id
from bwg360.tasks.jobs import query_ip

bp  = Blueprint('bwg360', __name__, template_folder='templates', static_folder='static', url_prefix='/')
sub = Blueprint('subdomain', __name__, template_folder='templates', static_folder='static', url_prefix='/', subdomain='www')

default_param = {"gettext": _}


@user_logged_in.connect_via(app)
def _track_login(sender, user, **extra):
    try:
        query_ip.delay(user.id, request.remote_addr)
    except Exception as e:
        print("query ip exception:", e)


@bp.route('', methods=['GET', 'POST'])
@sub.route('', methods=['GET', 'POST'])
@download_check
def home_page():
    if request.method == 'POST':
        form = SearchForm(request.form)
        if form.validate_on_submit():
            try:
                url_uuid = uuid.uuid1()                                                   # 一次搜索，一个uuid
            except ValueError:
                url_uuid = generate_crc_number(32)

            register = False
            timeout = 0 if register else app.config['CACHE_VISITOR_SEARCH_LIMIT']         # 若是游客，设置搜索结果超时机制
            redis_cache = MyRedisCache.getInstance()
            redis_cache.set(generate_flag(search_flag, url_uuid), form.file_url.data, timeout)

            return redirect(url_for('bwg360.search_page', uuid_key=url_uuid))
        else:
            flash(_('Please enter a valid URL'), 'error')
            return custom_render_template("page_home.html", form=form)
    else:
        form = SearchForm()
        return custom_render_template("page_home.html", form=form)


def _fetch_information(file_url):
    redis_cache = MyRedisCache.getInstance()
    details = redis_cache.get(generate_prefix(search_prefix, file_url), True)                        # 先从缓存中取
    if details:
        # #app.logger.info("hit the cache, return from cache")
        return details

    dler = make_file_dl(file_url)
    if dler:
        details = dler.fetch_url_details()                                     # 获取url的详细信息
        if isinstance(details, list):
            redis_cache.set(generate_prefix(search_prefix, file_url), details)  # 缓存 url-details

        return details
    else:
        return _('URL is not supported now!')


@bp.route('files/search/<string:uuid_key>', methods=['GET', ])
@sub.route('files/search/<string:uuid_key>', methods=['GET', ])
@download_check
def search_page(uuid_key):
    form = SearchForm()
    redis_cache = MyRedisCache.getInstance()
    file_url = redis_cache.get(generate_flag(search_flag, uuid_key))        # uuid:file_url键对, 未注册用户有5分钟超时
    if not file_url:
        flash(_("Please search by home page!"), 'error')
        return custom_render_template("page_home.html", form=form, gettext=_)

    form.file_url.data = file_url
    try:
        gl = gevent.spawn(_fetch_information, file_url)
        gl.join(5)                                              # 等待5s，如遇I/O block 会自动切换到其他greenlet
        result = gl.value
        if isinstance(result, list):
            fmts_form = FormatsForm()
            fmts_form.url_uuid = uuid_key
            fmts_form.file_url = file_url
            for dt in result:
                fmts_form.file_title = dt["file_title"]
                detail_form = DetailForm(dt=dt)
                fmts_form.video_fmts.append_entry(detail_form)

            form.file_url.data = ""                             # 清空搜索框
            return custom_render_template("page_home.html", title=fmts_form.file_title, form=form, fmts_form=fmts_form)
        else:
            if gl.exception:
                err_msg = gl.exception                          # 用于保存，真实的错误
                #app.logger.error(err_msg)
                flash(_('An error occurred, please try again later!'), 'error')
            elif isinstance(result, string_types):
                err_msg = result
                #app.logger.error(err_msg)
                flash(error_message_filter(err_msg), 'error')
            else:
                err_msg = 'Unknown error'
                #app.logger.error(err_msg)
                flash(_('An error occurred, please try again later!'), 'error')
            return custom_render_template("page_home.html", form=form, gettext=_)
    except gevent.Timeout as exc:
        flash(_('Fetch file information timeout, Please try again later!'), 'error')
        return custom_render_template("page_home.html", form=form, gettext=_)


@bp.route('files/<string:fid>/<string:uuid_key>', methods=['GET', ])
@sub.route('files/<string:fid>/<string:uuid_key>', methods=['GET', ])
@download_check
def show_download_page(fid, uuid_key):
    redis_cache = MyRedisCache.getInstance()
    url = redis_cache.get(generate_flag(search_flag, uuid_key))                  # uuid:file_url键对, 未注册用户有5分钟超时
    if url:
        one_download = {"fid": fid, "uuid": uuid_key}
        return custom_render_template("page_download.html", exist=True, form=one_download)  # will generate download-url
    else:
        return custom_render_template("page_download.html", exist=False, msg=_("URL does not exist!"))


@bp.route('files/download', methods=['GET', ])
@sub.route('files/download', methods=['GET', ])
@download_check
def file_download():
    redis_cache = MyRedisCache.getInstance()
    uuid_key = request.args.get('seq', None)
    file_url = redis_cache.get(generate_flag(search_flag, uuid_key))
    details  = redis_cache.get(generate_prefix(search_prefix, file_url), True)
    if uuid_key is None or not file_url or not details or not len(details):
        return custom_render_template("page_download.html", exist=False, msg=_("Waiting time is too long, timeout!"))

    # 免费下载文件不能大于500M
    format_id = request.args.get('fid')
    if is_free_download(current_user):
        file_size = get_file_size_of_format_id(file_url, format_id)
        if file_size > free_download_max_once:
            return custom_render_template("page_download.html", exist=False, msg=_("Free download can not be greater than %dM" % free_download_max_once))
        elif file_size < 0:
            return custom_render_template("page_download.html", exist=False, msg=_("An error occur when downloading"))

    # 开始下载
    ydl = make_file_dl(file_url, test_support=False)
    try:
        if not app.config['DEBUG']:
            redis_cache.delete(generate_flag(search_flag, uuid_key))                 # 非调试下，开始下载后，从缓存中删除本次的uuid

        # 直接传入current_user, on_close时获取不到正确的user对象，为NoneType
        username = 'anonymous' if current_user.is_anonymous else current_user.username
        user_info = (username, request.cookies.get('fppkcookie'), request.remote_addr)
        response = ydl.start_downloads(format_id, details[0], user_info)
        if isinstance(response, Response):
            return response
        elif isinstance(response, string_types):
            flash(response, 'error')
    except BaseException as e:
        print("exception is:{}".format(e))
        flash(_('Please enter a valid URL'), 'error')

    form = SearchForm()
    form.file_url.data = file_url                                                        # 用来在输入框显示 file_url
    return custom_render_template("page_home.html", form=form)


@bp.route('recharge/records', methods=['GET', ])
@sub.route('recharge/records', methods=['GET', ])
@login_required
def recharge_record():
    return custom_render_template("recharge_record.html")


@bp.route('download/records', methods=['GET', ])
@sub.route('download/records', methods=['GET', ])
@login_required
def download_record():
    show_limit = 25
    download_record_class = DownloadRecord.model()
    records = download_record_class.query.filter_by(user_id=current_user.id).order_by(download_record_class.time.desc()).limit(show_limit).all()
    now_tag = download_record_class.model_tag
    while len(records) < show_limit:
        remain = show_limit - len(records)
        pre_tag = DownloadRecord.previous_tag(now_tag)
        if pre_tag is None:
            break
        pre_download_record_class = DownloadRecord.model(pre_tag)
        pre_records = pre_download_record_class.query.filter_by(user_id=current_user.id).order_by(pre_download_record_class.time.desc()).limit(remain).all()
        records.extend(pre_records)
        now_tag = pre_tag
    return custom_render_template("download_record.html", records=records, limit=show_limit)


@bp.route('disclaimer', methods=['GET', ])
@sub.route('disclaimer', methods=['GET', ])
@login_required
def disclaimer():
    return custom_render_template("disclaimer.html")


@bp.route('support-lists', methods=['GET', ])
@sub.route('support-lists', methods=['GET', ])
@login_required
def support_list():

    return custom_render_template("support_list.html", lists=site_list)


@bp.route('do/recharge', methods=['GET', 'POST'])
@sub.route('do/recharge', methods=['GET', 'POST'])
@login_required
def do_recharge():
    return custom_render_template("do_recharge.html")


@bp.route('problem/tutorial', methods=['GET', ])
@sub.route('problem/tutorial', methods=['GET', ])
@login_required
def tutorial():
    return custom_render_template("tutorial.html")


@bp.route('problem/traffic', methods=['GET', ])
@sub.route('problem/traffic', methods=['GET', ])
@login_required
def traffic():
    return custom_render_template("traffic.html")


@bp.route('problem/download', methods=['GET', ])
@sub.route('problem/download', methods=['GET', ])
@login_required
def download():
    return custom_render_template("download_problem.html")


@bp.route('problem/file-cache', methods=['GET', ])
@sub.route('problem/file-cache', methods=['GET', ])
@login_required
def file_cache():
    return custom_render_template("file_cache.html")


# Register blueprint
add_blueprint(bp)
add_blueprint(sub)
