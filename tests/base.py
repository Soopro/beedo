# coding=utf-8
from __future__ import absolute_import

import unittest

import beedo
from utils.misc import now
from wx_apis.receive import wx_make_signature


# basic
class BasicTester(unittest.TestCase):

    @property
    def nonce(self):
        return u''

    @property
    def timestamp(self):
        return unicode(now())

    @property
    def token(self):
        return beedo.app.config['TOKEN']

    def signature(self, token, timestamp, nonce):
        return wx_make_signature(token, timestamp, nonce)

    def setUp(self):
        self.client = beedo.app.test_client()

    def tearDown(self):
        pass
