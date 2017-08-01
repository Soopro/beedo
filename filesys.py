# coding=utf8
from __future__ import absolute_import

import os


class Entry(dict):
    path = ''
    _id = ''

    def __init__(self, data, path):
        self.path = path
        self._id = data['_id']
        super(Entry, self).__init__(data)

    def save(self):
        filename = self..strip('/').strip('\\')
        file_path = os.path.join(yaml_dir, '{}.md'.format(filename))
        _file = self._data_encode(file_data)
        _file = {slug: v for k, v in _file.iteritems()}
        with open(file_path, 'w') as yaml_file:
            yaml.safe_dump(_file,
                           yaml_file,
                           default_flow_style=False,
                           indent=2,
                           allow_unicode=True)

    def delete(self):
        pass


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