# coding=utf-8
from __future__ import absolute_import


def register_blueprints(app):
    # register regular
    from .interface import blueprint as interface_module
    app.register_blueprint(interface_module, url_prefix='/interface')
