import os
# from flask import request
from flask import render_template

_translations_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'translations')

# Load BanYG360 translations, if Flask-BabelEx has been installed
try:
    from flask_babelex import Domain

    # Retrieve Flask-User translations from the flask_user/translations directory
    domain_translations = Domain(_translations_dir, domain='messages')
except ImportError:
    domain_translations = None


def gettext(string, **variables):
    return domain_translations.gettext(string, **variables) if domain_translations else string % variables


def lazy_gettext(string, **variables):
    return domain_translations.lazy_gettext(string, **variables) if domain_translations else string % variables


def get_language_codes():
    language_codes = []
    for folder in os.listdir(_translations_dir):
        locale_dir = os.path.join(_translations_dir, folder, 'LC_MESSAGES')
        if not os.path.isdir(locale_dir):
            continue
        language_codes.append(folder)
    return language_codes


def custom_render_template(*args, **kwargs):
    kwargs.update({"gettext": gettext})
    return render_template(*args, **kwargs)
