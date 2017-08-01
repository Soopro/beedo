# coding=utf8
from __future__ import absolute_import

import os
import yaml
import urllib


class Entry(dict):
    path = ''

    def __init__(self, data, path):
        self.path = path
        super(Entry, self).__init__(data)

    def save(self):
        _file = self._data_encode(dict(self))
        _file = {k.capitalize(): v for k, v in _file.iteritems()}
        if os.isfile(self.path):
            os.remove(self.path)
        with open(self.path, 'w') as yaml_file:
            yaml.safe_dump(_file,
                           yaml_file,
                           default_flow_style=False,
                           indent=2,
                           allow_unicode=True)
        return self['_id']

    def delete(self):
        if os.isfile(self.path):
            os.remove(self.path)
        return self['_id']

    def _data_encode(self, x):
        if isinstance(x, dict):
            return {k.lower(): self._data_encode(v)
                    for k, v in x.iteritems()}
        elif isinstance(x, list):
            return list([self._data_encode(i) for i in x])
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
