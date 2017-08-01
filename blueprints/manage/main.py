# coding=utf-8
from __future__ import absolute_import

from flask import Blueprint


blueprint = Blueprint('manage', __name__, template_folder='templates')


@blueprint.before_request
def before_request():
    pass
