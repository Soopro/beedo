# coding=utf-8
from __future__ import absolute_import

from flask import Flask, g, make_response
from flask.json import JSONEncoder

import os
import traceback

from loaders import (load_config, load_files, load_keys,
                     load_single_file, watch_files_date)
from services.i18n import Translator
from blueprints import register_blueprints


__version_info__ = ('1', '2', '0')
__version__ = '.'.join(__version_info__)

# create app
app = Flask(__name__)
app.version = __version__

load_config(app)

# create logs folder
logs_folder = app.config['LOGS_DIR']
if not os.path.isdir(logs_folder):
    os.makedirs(logs_folder)

# init app
app.debug = app.config.get('DEBUG', True)

# encoder
app.json_encoder = JSONEncoder

# register blueprints
register_blueprints(app)


# data
app.db = dict()
app.db['files'] = load_files(app)
app.db['keys'] = load_keys(app, app.db['files'])
app.db['modifications'] = watch_files_date(app)


# languages
lang_dir = app.config.get('LANGUAGES_DIR')
locale = app.config.get('LOCALE')
translator = Translator(locale, lang_dir)
app.jinja_env.globals.update(_=translator.gettext)


@app.before_request
def app_before_request():
    modifications = watch_files_date(app)
    # check added / modified
    for k, v in modifications.iteritems():
        modified = app.db['modifications'].get(k)
        if not modified or modified['modified'] != v['modified']:
            if not modified:
                print 'added -->', v['_id']
            else:
                print 'modified -->', v['_id']
            file_id = v['_id']
            file_data = load_single_file(k, v['_id'])
            if file_data:
                app.db['files'][file_id] = file_data
                for key in file_data['keywords']:
                    app.db['keys'][key] = file_id
    # check removed
    for k, v in app.db['modifications'].iteritems():
        if k not in modifications:
            print 'removed -->', v['_id']
            removed = app.db['files'].get(v['_id'])
            if removed:
                for key in removed['keywords']:
                    if app.db['keys'].get(key) == removed['_id']:
                        del app.db['keys'][key]
                del app.db['files'][v['_id']]

    app.db['modifications'] = modifications

    g.files = app.db['files']
    g.keys = app.db['keys']


@app.errorhandler(Exception)
def errorhandler(err):
    err_msg = '{}\n{}'.format(repr(err), traceback.format_exc())
    app.logger.error(err_msg)
    return make_response(repr(err), 500)


if __name__ == '__main__':
    host = app.config.get('HOST')
    port = app.config.get('PORT')

    print '-------------------------------------------------------'
    print 'Beedo: {}'.format(app.version)
    print '-------------------------------------------------------'

    app.run(host=host, port=port, debug=True, threaded=True)
