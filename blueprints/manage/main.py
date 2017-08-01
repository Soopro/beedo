# coding=utf-8
from __future__ import absolute_import

from flask import Blueprint, current_app, make_response
import traceback


bp_name = 'response'

blueprint = Blueprint(bp_name, __name__)


@blueprint.before_request
def before_request():
    pass


@blueprint.errorhandler(Exception)
def errorhandler(err):
    err_msg = '{}\n{}'.format(repr(err), traceback.format_exc())
    current_app.logger.error(err_msg)
    return make_response(repr(err), 500)
