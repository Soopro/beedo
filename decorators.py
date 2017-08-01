# coding=utf-8
from __future__ import absolute_import

from functools import wraps
from flask import current_app, session, redirect, url_for
from utils.misc import hmac_sha


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        secret_key = current_app.secret_key
        identity = current_app.config['IDENTITY']
        if not session.get('identity'):
            return redirect(url_for('manage.login'))
        elif session['identity'] != hmac_sha(secret_key, identity):
            session.clear()
            raise Exception(u'Session has expired. Please login again.')
        return f(*args, **kwargs)
    return wrapper
