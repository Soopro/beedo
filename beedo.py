# coding=utf-8
from __future__ import absolute_import

from flask import Flask, g, make_response
from flask.json import JSONEncoder

import os
import traceback

from loaders import load_config, load_files, load_keys
from services.i18n import Translator
from blueprints import register_blueprints


__version_info__ = ('1', '1', '1')
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


# languages
lang_dir = app.config.get('LANGUAGES_DIR')
locale = app.config.get('LOCALE')
translator = Translator(locale, lang_dir)
app.jinja_env.globals.update(_=translator.gettext)


@app.before_request
def app_before_request():
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
