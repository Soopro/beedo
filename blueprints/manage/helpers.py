# coding=utf-8
from __future__ import absolute_import

from flask import current_app
import os


def make_file_path(file_id):
    content_dir = current_app.config.get('DATA_DIR')
    content_ext = current_app.config.get('DATA_FILE_EXT')
    return os.path.join(content_dir, u'{}{}'.format(file_id, content_ext))
