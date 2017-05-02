# coding=utf-8
from __future__ import absolute_import

import json
import os
from .helpers import write_to_yaml


def load_json_data(path):
    print '----------- Load JSON data -----------'
    try:
        with open(path) as wp_json:
            wp_meta_data = json.load(wp_json)
    except Exception as e:
        err_msg = 'Load WP data failed: {}'.format(str(e))
        raise Exception(err_msg)
    # init files
    static_trigger = ['subscribe', 'default']
    reserved_file_ids = []
    files = {}
    for data in wp_meta_data:
        _id = data['post_id']
        if _id not in files:
            files[_id] = {
                'keys': [],
                'type': u'',
                'status': 1,
                'text': u'',
                'messages': [],
            }
        if data.get('meta_key') == '_trigger' and \
           data.get('meta_value') in static_trigger:
            reserved_file_ids.append({
                '_id': _id,
                'slug': data.get('meta_value')
            })
        if data.get('meta_key') == '_type':
            files[_id]['type'] = data.get('meta_value')
        if data.get('meta_key') == '_keyword':
            files[_id]['keys'] += data.get('meta_value').split(',')
        if data.get('meta_key') == '_content':
            files[_id]['text'] = data.get('meta_value')
        if data.get('meta_key') == '_phmsg_item':
            msg = data.get('meta_value')
            if not isinstance(msg, dict):
                msg = json.loads(msg)
            files[_id]['messages'].append({
                'title': msg.get('title', u''),
                'description': msg.get('des', u''),
                'picurl': msg.get('pic', u''),
                'url': msg.get('url', u''),
            })

    # make reserved
    for rf in reserved_file_ids:
        f = files.pop(rf.get('_id'), None)
        if f:
            files[rf.get('slug')] = f
    # write
    write_to_yaml(files, os.path.dirname(path))
