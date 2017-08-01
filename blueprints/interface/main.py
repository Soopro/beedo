# coding=utf-8
from __future__ import absolute_import

from flask import Blueprint


blueprint = Blueprint('interface', __name__)


@blueprint.before_request
def before_request():
    pass
