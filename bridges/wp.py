# coding=utf-8
from __future__ import absolute_import

import json


def load_json_data(path):
    try:
        with open(path) as wp_json:
            wp_data = json.load(wp_json)
    except Exception as e:
        err_msg = 'Load WP data failed: {}'.format(str(e))
        raise Exception(err_msg)
    print wp_data
