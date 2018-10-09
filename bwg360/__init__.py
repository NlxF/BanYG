# -*- coding: utf-8 -*-
from flask import Flask, g, session, abort
from flask_cache import Cache
from flask_babelex import Babel
from flask_moment import Moment
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from flask_debugtoolbar import DebugToolbarExtension
from bwg360.util import filters
from bwg360.util import myalarm
from bwg360.util.translation_utils import custom_render_template
from bwg360.util.mycache import MyRedisCache, get_free_download_size
from bwg360.util.plugHelper import register_blueprints
from bwg360.util.mySqlalchemy import UnlockedReadAlchemy
from bwg360.util.makeCelery import make_celery
from celery.utils.log import get_task_logger
from bwg360.util.utils import setup_logger, setup_login_user, setup_list_support_site

# ***** Initialize Flask app  *****#

app = Flask("bwg360")

# ***** Initialize app config settings *****#
app.config.from_object('bwg360.bwg360_settings')

celery = make_celery(app)
celery_logger = get_task_logger(__name__)       # celery logger

db = UnlockedReadAlchemy(app)
csrf = CSRFProtect(app)
app_cache = None


# 参考 http://flask.pocoo.org/docs/0.11/api/
@app.errorhandler(404)
def page_not_found(e):
    return custom_render_template('404.html'), 404


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return custom_render_template('error.html', reason=e.description), 400


@app.before_request
def before_request():
    g.amount = get_free_download_size()


@app.before_first_request
def before_first_request():
    # init free download
    # myalarm.init_free_download()
    pass


# configure app
def create_app(db_command=False):

    app.config['DEBUG'] = True if app.env == 'development' else False

    # ***** Initialize app config settings *****
    # app.config.from_object('bwg360.bwg360_settings')

    if not app.config['DEBUG']:
        app.config.from_object('bwg360.bwg360_deploy')

    app.config['WTF_CSRF_ENABLED'] = not app.config['DEBUG']   # Disable CSRF checks while Debug

    # Configure app extensions

    # Setup logger
    setup_logger(app)

    # Setup Cache
    global app_cache
    app_cache = Cache(app)

    # Setup i18n
    # flask_babelex init need before flask_user
    babel = Babel(app)

    # Setup Flask-User
    setup_login_user(app, db)

    # Setup support site
    setup_list_support_site()

    # Setup custom cache
    MyRedisCache(app.config['CACHE_REDIS_HOST'],
                 app.config['CACHE_REDIS_PORT'],
                 app.config['CACHE_REDIS_PASSWORD'],
                 app.config['CACHE_REDIS_DB'],
                 app.config['MYREDIS_DEFAULT_TIMEOUT'])

    # custom time
    moment = Moment(app)

    # migrate db
    migrate = Migrate(app, db)

    if not db_command:
        # Free-Download size
        myalarm.init_free_download()

    # Setup DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)

    # celery setting
    celery.conf.update(app.config)        # 更新 celery 的配置

    # Define bootstrap_is_hidden_field for flask-bootstrap's bootstrap_wtf.html
    from wtforms.fields import HiddenField

    def is_hidden_field_filter(field):
        return isinstance(field, HiddenField)

    app.jinja_env.globals['bootstrap_is_hidden_field'] = is_hidden_field_filter

    # load blueprints
    register_blueprints(app)

    # register custom filter
    app.jinja_env.filters['human_readable'] = filters.sizeof_fmt
    app.jinja_env.filters['transform'] = filters.transform
    app.jinja_env.filters['readable'] = filters.readable

    return app
