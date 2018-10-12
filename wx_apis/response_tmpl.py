# coding=utf-8
from __future__ import absolute_import

import time
import HTMLParser


class WxResponseTmpl(object):
    def __init__(self, to_user, from_user):
        self.to_user = to_user
        self.from_user = from_user
        return

    def render(self):
        return ''


class WxTextResponseTmpl(WxResponseTmpl):
    tmpl = u'''
    <xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%d</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    </xml>
    '''

    def __init__(self, to_user, from_user, content, json_mode=False):
        super(WxTextResponseTmpl, self).__init__(to_user, from_user)
        self.json_mode = json_mode
        self.content = content or u''
        return

    def render(self):
        if self.json_mode:
            result = {
                'touser': self.to_user,
                'msgtype': 'text',
                'text': {
                    'content': self.content[:600]
                }
            }
        else:
            result = self.tmpl % (self.to_user,
                                  self.from_user,
                                  int(time.time()),
                                  self.content)
        return result


class WxNewsResponseTmpl(WxResponseTmpl):

    MAX_ITEMS = 1  # fucked by wechat api, they turn max 8 to 1.

    tmpl = u'''
    <xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%d</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <ArticleCount>%d</ArticleCount>
    <Articles>%s</Articles>
    </xml>
    '''

    tmpl_item = u'''
    <item>
    <Title><![CDATA[%s]]></Title>
    <Description><![CDATA[%s]]></Description>
    <PicUrl><![CDATA[%s]]></PicUrl>
    <Url><![CDATA[%s]]></Url>
    </item>'''

    def __init__(self, to_user, from_user, items, json_mode=False):
        super(WxNewsResponseTmpl, self).__init__(to_user, from_user)

        self.json_mode = json_mode

        if not isinstance(items, list):
            items = []
        self.items = [{
            'title': item.get('title') or u'',
            'content': item.get('content') or u'',
            'picurl': item.get('picurl') or u'',
            'url': item.get('url') or u'',
        } for item in items][:self.MAX_ITEMS]

        return

    def render_item(self):
        html_parser = HTMLParser.HTMLParser()
        unescape = html_parser.unescape

        if self.json_mode:
            result = []
            for item in self.items:
                result.append({
                    'title': unescape(item['title']),
                    'description': unescape(item['content']),
                    'picurl': item['picurl'],
                    'url': item['url']
                })
        else:
            item_str_list = [self.tmpl_item % (
                             unescape(item['title']),
                             unescape(item['content']),
                             item['picurl'],
                             item['url']
                             ) for item in self.items]

            result = ''.join(item_str_list)
        return result

    def render(self):
        if self.json_mode:
            result = {
                'touser': self.to_user,
                'msgtype': 'news',
                'news': {
                    'articles': self.render_item()
                }
            }
        else:
            result = self.tmpl % (self.to_user,
                                  self.from_user,
                                  int(time.time()),
                                  len(self.items),
                                  self.render_item())
        return result
