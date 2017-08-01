# coding=utf-8
from __future__ import absolute_import

from flask import Flask, g, make_response
from flask.json import JSONEncoder

import os
import traceback

from loaders import load_config, load_files, load_keys
from blueprints import register_blueprints


__version_info__ = ('0', '2', '0')
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
DATA = dict()
DATA['files'] = load_files(app)
DATA['keys'] = load_keys(app, DATA['files'])


@app.before_request
def app_before_request():
    g.keys = DATA['keys']
    g.files = DATA['files']


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
