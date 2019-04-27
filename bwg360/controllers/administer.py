# -*- coding: utf-8 -*-
from flask import Blueprint, request
from flask_user import current_user, login_required, roles_accepted
from bwg360 import db, app
from bwg360.util.translation_utils import custom_render_template
from bwg360.util.plugHelper import add_blueprint
from bwg360.util.mycache import MyRedisCache, CacheSetting
from bwg360.util.decorators import permission_check


bp  = Blueprint('admin', __name__, template_folder='templates', static_folder='static', url_prefix='/m')


@bp.route('', methods=['GET', 'POST'])
@permission_check
def administer_page():
    if request.method == 'POST':
        st = CacheSetting.getInstance()
        return custom_render_template("page_administer.html")
    else:
        st = CacheSetting.getInstance()
        return custom_render_template("page_administer.html")


# Register blueprint
add_blueprint(bp)

