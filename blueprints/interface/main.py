# coding=utf-8
from __future__ import absolute_import

from flask import Blueprint, current_app, make_response
import traceback

from utils.misc import route_inject

from .routes import urlpatterns


bp_name = 'response'

blueprint = Blueprint(bp_name, __name__)
route_inject(blueprint, urlpatterns)


@blueprint.before_request
def before_request():
    pass


@blueprint.errorhandler(Exception)
def errorhandler(err):
    err_msg = '{}\n{}'.format(repr(err), traceback.format_exc())
    current_app.logger.error(err_msg)
    return make_response(repr(err), 500)
