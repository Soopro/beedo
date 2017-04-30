#coding=utf-8
from .WXBizMsgCrypt import WXBizMsgCrypt


class WechatCrypt(object):
    def __init__(self, wx_token, encodingAESKey, wx_appid):
        self.wx_token = wx_token
        self.encodingAESKey = encodingAESKey
        self.wx_appid = wx_appid
        self.crypt_instance = WXBizMsgCrypt(self.wx_token,
                                            self.encodingAESKey,
                                            self.wx_appid)

    def encrypt_msg(self, to_xml, nonce):
        ret, encrypt_xml = self.crypt_instance.EncryptMsg(to_xml, nonce)
        if ret == 0:
            return encrypt_xml
        return

    def decrypt_msg(self, from_xml, msg_sign, timestamp, nonce):
        ret, decryp_xml = self.crypt_instance.DecryptMsg(from_xml, msg_sign,
                                                         timestamp, nonce)
        if ret == 0:
            return decryp_xml
        return
