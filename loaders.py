# coding=utf8
from __future__ import absolute_import

import os
import yaml


def load_config(app, config_name='config.py'):
    app.config.from_pyfile(config_name)
    app.config.setdefault('DEBUG', False)
    app.config.setdefault('HOST', '0.0.0.0')
    app.config.setdefault('PORT', 5500)
    app.config.setdefault('CONTENT_DIR', 'content')
    app.config.setdefault('CONTENT_FILE_EXT', '.md')

    app.config.setdefault('WX_TOKEN', u'token')
    app.config.setdefault('APP_ID', u'')
    app.config.setdefault('ENCODING_AES_KEY', u'')

    app.config.setdefault('DEFAULT_MESSAGE', u'...')


def load_files(app):
    content_dir = app.config.get('CONTENT_DIR')
    content_ext = app.config.get('CONTENT_FILE_EXT')

    all_files = []
    for root, directory, files in os.walk(content_dir):
        file_full_paths = [
            os.path.join(root, f)
            for f in filter(lambda x: x.endswith(content_ext), files)
        ]
        all_files.extend(file_full_paths)

    file_data = {}
    for f in all_files:
        relative_path = f.split(content_dir + '/', 1)[1]
        if relative_path.startswith('_'):
            print '***', f
            continue
        print '-->', f
        with open(f, 'r') as fh:
            meta_string = fh.read().decode('utf-8')
        try:
            meta = _parse_file_meta(meta_string)
        except Exception as e:
            e.current_file = f
            raise e

        file_id = f.replace(content_dir + '/', '', 1).strip('/')
        items = [_prase_news_item(item) for item in meta.pop('items', [])]
        file_data.update({
            file_id: {
                'keys': meta.pop('keys', []),
                'status': meta.pop('status', 1),
                'text': meta.pop('text', u''),
                'news': items[:8],  # max 8 entries
            }
        })

    print '<-- Data Loaded -->'

    return file_data


def load_keys(file_data):
    keys_data = {}
    for k, v in file_data.iteritems():
        for key in v.get('keys', [])[:60]:
            if not isinstance(key, basestring) or key in keys_data:
                print 'Conflict ------------>'
                print key, ': ', keys_data.get(key)
                print '<---------------------'
                continue
            print '-->', key
            keys_data.update({key: k})
    print '<-- Keywords Loaded -->'
    return keys_data


# helpers
def _prase_news_item(item):
        return {
            'title': item.get('title', u''),
            'description': item.get('description', u''),
            'picurl': item.get('picurl', u''),
            'url': item.get('url', u''),
        }


def _parse_file_meta(meta_string):
    def convert_data(x):
        if isinstance(x, dict):
            return dict((k.lower(), convert_data(v))
                        for k, v in x.iteritems())
        elif isinstance(x, list):
            return list([convert_data(i) for i in x])
        elif isinstance(x, str):
            return x.decode('utf-8')
        elif isinstance(x, (unicode, int, float, bool)) or x is None:
            return x
        else:
            try:
                x = str(x).decode('utf-8')
            except Exception as e:
                print e
                pass
        return x
    yaml_data = yaml.safe_load(meta_string)
    headers = convert_data(yaml_data)
    return headers
