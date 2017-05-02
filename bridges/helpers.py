# coding=utf-8
from __future__ import absolute_import

import yaml
import urllib
import os


def write_to_yaml(files, base_dir):
    if not isinstance(files, dict):
        raise Exception('file not a dict')
    yaml_dir = os.path.join(base_dir.strip('/').strip('\\'), 'yaml')
    if not os.path.isdir(yaml_dir):
        os.makedirs(yaml_dir)

    for filename, file_data in files.iteritems():
        filename = filename.strip('/').strip('\\')
        file_path = os.path.join(yaml_dir, '{}.md'.format(filename))
        _file = _data_encode(file_data)
        _file = {k.capitalize(): v for k, v in _file.iteritems()}
        with open(file_path, 'w') as yaml_file:
            yaml.safe_dump(_file,
                           yaml_file,
                           default_flow_style=False,
                           indent=2,
                           allow_unicode=True)
        print '==>', file_path


def _data_encode(x):
    if isinstance(x, dict):
        return {k.lower(): _data_encode(v)
                for k, v in x.iteritems()}
    elif isinstance(x, list):
        return list([_data_encode(i) for i in x])
    elif isinstance(x, unicode):
        return urllib.unquote(x.encode('utf-8'))
    elif isinstance(x, str):
        return urllib.unquote(x)
    elif isinstance(x, (int, float, bool)) or x is None:
        return x
    else:
        try:
            x = urllib.unquote(str(x))
        except Exception as e:
            print e
            pass
    return x
