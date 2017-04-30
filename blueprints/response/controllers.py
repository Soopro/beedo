# coding=utf-8
from __future__ import absolute_import

from flask import current_app, request

from wx_apis.crypt import WechatCrypt
from wx_apis.receive import wx_request_validate, wx_parse_xml
from wx_apis.response_tmpl import (WxTextResponseTmpl,
                                   WxNewsResponseTmpl)
from .helpers import get_response


def check(token):
    wx_token = current_app.config['TOKEN']
    if not wx_request_validate(wx_token) or wx_token != token:
        return 'error'
    return request.args.get('echostr', '')


def receive(token):
    wx_token = current_app.config['TOKEN']
    wx_appid = current_app.config['APP_ID']
    encodingAESKey = current_app.config['ENCODING_AES_KEY']
    if not wx_request_validate(wx_token) or wx_token != token:
        return 'error'
    # decrypt if encrypt_type is aes
    if request.args.get('encrypt_type') == 'aes':
        if not wx_appid or not encodingAESKey:
            return 'error'
        wechat_crypt = WechatCrypt(wx_token,
                                   encodingAESKey.encode('utf-8'),
                                   wx_appid.encode('utf-8'))
        request_data = _decrypt_receive_data(request.data, wechat_crypt)
    else:
        wechat_crypt = None
        request_data = request.data

    msg = wx_parse_xml(request_data)

    # parse trigger
    if msg.get('msg_type') == 'event' and msg.get('event') == 'unsubscribe':
        return 'unsubscribe'

    trigger = {
        'type': 'default',
        'key': None,
    }

    receive_type = msg.get('msg_type')

    if receive_type == 'text':
        trigger['type'] = 'keywords'
        trigger['key'] = msg.get('content', u'').lower()[:60]
    elif receive_type == 'event':
        if msg.get('event') == 'subscribe':
            trigger['type'] = 'subscribe'
            trigger['key'] = None
        else:
            trigger['type'] = 'keywords'
            trigger['key'] = msg.get('event_key', u'')

    # find response
    response = get_response(trigger)
    print response
    # first round find response contents
    response_msg = _make_response_msg(response, msg, trigger)

    # output
    if isinstance(response_msg, basestring):
        if request.args.get('encrypt_type') == 'aes':
            response_msg = _encrypt_response_data(response_msg, wechat_crypt)
    else:
        response_msg = ''

    return response_msg or current_app.config.get('DEFAULT_MESSAGE')


def _make_response_msg(resp, msg, trigger, default=None):
    to_user = msg.get('from_user_name')
    from_user = msg.get('to_user_name')

    if not isinstance(resp, dict) or 'type' not in resp:
        return ''

    resp_instance = None
    if resp['type'] == 'text':
        resp_instance = WxTextResponseTmpl(to_user,
                                           from_user,
                                           resp['text'])
    elif resp['type'] == 'news':
        resp_instance = WxNewsResponseTmpl(to_user,
                                           from_user,
                                           resp['messages'])
    if resp_instance:
        msg = resp_instance.render()
    else:
        msg = ''

    return msg


def _decrypt_receive_data(receive_data, wechat_crypt):
    if not wechat_crypt:
        return receive_data
    return wechat_crypt.decrypt_msg(receive_data,
                                    request.args.get('msg_signature'),
                                    request.args.get('timestamp'),
                                    request.args.get('nonce'))


def _encrypt_response_data(response_data, wechat_crypt):
    if not wechat_crypt:
        return response_data
    return wechat_crypt.encrypt_msg(response_data.encode('utf-8'),
                                    request.args.get('nonce'))
