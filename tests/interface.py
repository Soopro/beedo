# coding=utf-8
from __future__ import absolute_import

from utils.misc import now
from .base import BasicTester


# interface
class InterfaceTester(BasicTester):
    # check
    def test_check(self):
        echostr = u'test-check'
        token = u'token'
        timestamp = unicode(now())
        nonce = u''
        signature = self._signature(token, timestamp, nonce)
        url = '/interface/{0}?signature={1}&timestamp={2}&nonce={3}' + \
              '&echostr={4}'
        url = url.format(token, signature, timestamp, nonce, echostr)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(resp.data, 'error')

    def test_check_wrong_signature(self):
        echostr = u'test-check'
        token = u'token'
        timestamp = unicode(now())
        nonce = u''
        signature = 'wrong_signature'
        url = '/interface/{0}?signature={1}&timestamp={2}&nonce={3}' + \
              '&echostr={4}'
        url = url.format(token, signature, timestamp, nonce, echostr)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, 'error')

    # receive
    def test_receive(self):
        pass
