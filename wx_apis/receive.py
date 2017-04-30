# coding=utf-8
from __future__ import absolute_import

from flask import request

import hashlib
from inflection import underscore
import xml.etree.cElementTree as ET


def wx_request_validate(token):
    if token is None:
        return False
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    return _check_signature(signature, token, timestamp, nonce)


def _check_signature(signature, token, timestamp, nonce):
    ln = [token, timestamp, nonce]
    ln = sorted(ln)
    base = ''.join(ln)
    signed = hashlib.sha1(base)
    return signed.hexdigest() == signature


def wx_parse_xml(body):
    tree = ET.fromstring(body)

    result = dict()
    for child in tree.getchildren():
        tag = underscore(child.tag)
        text = child.text
        if not isinstance(text, unicode):
            text = unicode(text)
        result[tag] = text

    return result
