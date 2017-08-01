# coding=utf-8
from __future__ import absolute_import

from flask import g


def get_response(trigger):
    if trigger['type'] == 'subscribe':
        response = g.files.get('subscribe')
    elif trigger['type'] == 'keywords':
        file_id = g.keys.get(trigger['key'])
        if file_id:
            response = g.files.get(file_id)
        else:
            response = None
    if not response:
        response = g.files.get('default')
    return response


def get_append_resp():
    return g.files.get('appends')
