# coding=utf-8
from __future__ import absolute_import

DEBUG = True

HOST = '0.0.0.0'
PORT = 6002

DATA_DIR = 'data'
LOCALE = 'zh'

# WX config
TOKEN = u'token'
"""
The interface url will be:
<your-domain-url>/interface/<token>
"""

APP_ID = u''
ENCODING_AES_KEY = u''

# defaults
DEFAULT_MESSAGE = u'...'
STATIC_FILENAME = ('subscribe', 'default', 'appends')

# security
SECRET_KEY = 'ai!ovcz>8_^Q]}7|WZsy'
IDENTITY = 'beedo1985'
