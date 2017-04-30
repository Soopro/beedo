# coding=utf-8
from __future__ import absolute_import


def register_blueprints(app):
    # register regular
    from .response import blueprint as response_module
    app.register_blueprint(response_module)
