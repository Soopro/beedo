# coding=utf-8
from __future__ import absolute_import

from utils.misc import add_url_params
from .base import BasicTester


# interface
class InterfaceTester(BasicTester):
    # check
    def test_check(self):
        params = {
            'signature': self.signature(self.token,
                                        self.timestamp,
                                        self.nonce),
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'echostr': u'test-check',
        }
        url = '/interface/{0}'.format(self.token)
        url = add_url_params(url, params)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(resp.data, 'error')
        self.assertEqual(resp.data, 'test-check')

    def test_check_wrong_signature(self):
        params = {
            'signature': u'wrong_signature',
            'timestamp': self.timestamp,
            'nonce': u'',
            'echostr': u'test-check',
        }
        url = '/interface/{0}'.format(self.token)
        url = add_url_params(url, params)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, 'error')

    # receive
    def test_receive(self):
        params = {
            'signature': self.signature(self.token,
                                        self.timestamp,
                                        self.nonce),
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'echostr': u'test-check',
        }
        post_xml = '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[testsearch]]></Content>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        url = '/interface/{0}'.format(self.token)
        url = add_url_params(url, params)
        resp = self.client.post(url, data=post_xml)
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(resp.data, 'error')
        print 'default ---->'
        print resp.data

    def test_receive_a_key(self):
        params = {
            'signature': self.signature(self.token,
                                        self.timestamp,
                                        self.nonce),
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'echostr': u'test-check',
        }
        post_xml = '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[fuck]]></Content>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        url = '/interface/{0}'.format(self.token)
        url = add_url_params(url, params)
        resp = self.client.post(url, data=post_xml)
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(resp.data, 'error')
        print 'key ---->'
        print resp.data
