# -*- coding: utf-8 -*-
from bwg360.util.translation_utils import lazy_gettext as _
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, FormField, FieldList, IntegerField
from wtforms.validators import DataRequired, URL
from wtforms import StringField, SubmitField


class DetailForm(FlaskForm):
    file_ext = StringField('file_ext')
    file_size = IntegerField('file_size')
    file_format = StringField('file_format')
    file_format_id = StringField('file_format_id')

    def __init__(self, dt=None, *args, **kwargs):
        super(DetailForm, self).__init__(*args, **kwargs)
        if isinstance(dt, dict):
            self.file_ext = dt.get("file_ext")
            self.file_size = dt.get("file_size")
            self.file_format = dt.get("file_format")
            self.file_format_id = dt.get("file_format_id")


class FormatsForm(FlaskForm):
    file_url = StringField('Video URL', validators=[DataRequired(), URL()])
    url_uuid = StringField('URL UUID')
    file_title = StringField('video title')
    video_fmts = FieldList(FormField(DetailForm))


class SearchForm(FlaskForm):
    file_url = StringField(label=_('Input video or file URL'), validators=[DataRequired(), URL()])

    # recaptcha = RecaptchaField()


