# coding=utf-8
from __future__ import absolute_import

import unittest
import hashlib

from beedo import app as beedo


# basic
class BasicTester(unittest.TestCase):
    def _signature(self, token, timestamp, nonce):
        ln = [token, timestamp, nonce]
        ln = sorted(ln)
        base = ''.join(ln)
        signed = hashlib.sha1(base)
        return signed.hexdigest()

    def setUp(self):
        self.client = beedo.test_client()

    def tearDown(self):
        pass
