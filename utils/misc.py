# coding=utf-8
from __future__ import absolute_import

from slugify import slugify
from datetime import datetime
from functools import cmp_to_key

import re
import time
import hashlib
import hmac


def route_inject(app_or_blueprint, url_patterns):
    for pattern in url_patterns:
        options = pattern[3] if len(pattern) > 3 else {}
        app_or_blueprint.add_url_rule(pattern[0],
                                      view_func=pattern[1],
                                      methods=pattern[2].split(),
                                      **options)


def process_slug(value, ensure=True):
    try:
        slug = unicode(slugify(value))
    except Exception:
        slug = u''
    if not slug and ensure:
        slug = unicode(repr(time.time())).replace('.', '-')
    return slug


def now(dig=10):
    if dig == 10:
        return int(time.time())
    elif dig == 11:
        return int(time.time() * 10)
    elif dig == 12:
        return int(time.time() * 100)
    elif dig == 13:
        return int(time.time() * 1000)
    elif dig == 14:
        return int(time.time() * 10000)
    elif dig == 15:
        return int(time.time() * 100000)
    elif dig == 16:
        return int(time.time() * 1000000)
    else:
        return time.time()


def remove_multi_space(text):
    if isinstance(text, str):
        text = text.decode('utf-8')
    elif not isinstance(text, unicode):
        return u''
    return re.sub(r'\s+', ' ', text).replace('\n', ' ').replace('\b', ' ')


def sortedby(source, sort_keys, reverse=False):
    sorts = []
    if not isinstance(sort_keys, list):
        sort_keys = [sort_keys]

    def parse_sorts(key):
        if isinstance(key, tuple):
            sorts.append((key[0], key[1]))
        elif isinstance(key, basestring):
            if key.startswith('-'):
                key = key.lstrip('-')
                direction = -1
            else:
                key = key.lstrip('+')
                direction = 1
            sorts.append((key, direction))

    for key in sort_keys:
        parse_sorts(key)

    def compare(a, b):
        for sort in sorts:
            key = sort[0]
            direction = sort[1]
            if a.get(key) < b.get(key):
                return -1 * direction
            if a.get(key) > b.get(key):
                return 1 * direction
        return 0

    return sorted(source, key=cmp_to_key(compare), reverse=reverse)


def parse_int(num, default=0, natural=False):
    if not isinstance(default, int):
        default = 0
    if not isinstance(natural, (int, bool)):
        natural = False
    try:
        num = int(float(num))
    except Exception:
        num = default
    if natural == 0:
        num = max(0, num)
    elif natural:
        num = max(1, num)
    return num


def file_md5(fname):
    _hash = hashlib.md5()
    with open(fname, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            _hash.update(chunk)
    return _hash.hexdigest()


def hmac_sha(key, msg, digestmod=None, output=True):
    if digestmod is None:
        digestmod = hashlib.sha1
    sha = hmac.new(str(key), str(msg), digestmod=digestmod)
    if output:
        return sha.hexdigest()
    else:
        return sha


def format_date(date, to_format, input_datefmt='%Y-%m-%d'):
    if not to_format:
        return date
    if isinstance(date, basestring):
        try:
            date_object = datetime.strptime(date, input_datefmt)
        except Exception:
            return date

    elif isinstance(date, int):
        if len(str(date)) == 13:
            date = int(date / 1000)
        try:
            date_object = datetime.fromtimestamp(date)
        except Exception:
            return date
    else:
        return date

    try:
        _formatted = date_object.strftime(to_format.encode('utf-8'))
        date_formatted = _formatted.decode('utf-8')
    except Exception:
        date_formatted = date
    return date_formatted


def str2unicode(text):
    if isinstance(text, str):
        return text.decode('utf-8')
    return text


def unicode2str(text):
    if isinstance(text, unicode):
        return text.encode('utf-8')
    return text


def match_cond(target, cond_key, cond_value, force=True, opposite=False):
    """
    params:
    - target: the source data want to check.
    - cond_key: the attr key of condition.
    - cond_value: the value of condition.
      if the cond_value is a list, any item matched will make output matched.
    - opposite: reverse check result.
    - force: must have the value or not.
    """

    def _dotted_get(key, obj):
        if not isinstance(obj, dict):
            return None
        elif '.' not in key:
            return obj.get(key)
        else:
            key_pairs = key.split('.', 1)
            obj = obj.get(key_pairs[0])
            return _dotted_get(key_pairs[1], obj)

    def _dotted_in(key, obj):
        if not isinstance(obj, dict):
            return False
        elif '.' not in key:
            return key in obj
        else:
            key_pairs = key.split('.', 1)
            obj = obj.get(key_pairs[0])
            return _dotted_in(key_pairs[1], obj)

    if cond_value == '' and not force:
        return _dotted_in(cond_key, target) != opposite
    elif cond_value is None and not force:
        # if cond_value is None will reverse the opposite,
        # then for the macthed opposite must reverse again. so...
        # also supported if the target value really is None.
        return _dotted_in(cond_key, target) == opposite
    elif isinstance(cond_value, bool) and not force:
        return _dotted_in(cond_key, target) != opposite
    elif not _dotted_in(cond_key, target):
        return False

    matched = False
    target_value = _dotted_get(cond_key, target)
    if isinstance(cond_value, list):
        for c_val in cond_value:
            matched = match_cond(target, cond_key, c_val, force=True)
            if matched:
                break
    elif isinstance(cond_value, bool):
        target_bool = isinstance(target_value, bool)
        matched = cond_value == target_value and target_bool
    else:
        if isinstance(target_value, list):
            matched = cond_value in target_value
        else:
            matched = cond_value == target_value

    return matched != opposite
