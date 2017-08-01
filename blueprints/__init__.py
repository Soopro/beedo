# coding=utf-8
from __future__ import absolute_import


def register_blueprints(app):
    # register interface
    from .interface import blueprint as interface_module
    app.register_blueprint(interface_module, url_prefix='/interface')

    # register manage
    from .manage import blueprint as manage_module
    app.register_blueprint(manage_module, url_prefix='/manage')
