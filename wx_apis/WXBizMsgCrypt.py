# coding=utf-8

from Crypto.Cipher import AES
import xml.etree.cElementTree as ET
import base64
import string
import random
import hashlib
import time
import struct
import socket
import ierror
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

"""
About Crypto.Cipher module, ImportError: No module named 'Crypto' solutions
Go to the official website https://www.dlitz.net/software/pycrypto/
download pycrypto.
After downloading, follow the instructions in the README "Installation"
section of conduct pycrypto installation.
"""


class FormatException(Exception):
    pass


def throw_exception(message, exception_class=FormatException):
    """my define raise exception function"""
    raise exception_class(message)


class SHA1:
    """signature"""

    def getSHA1(self, token, timestamp, nonce, encrypt):
        """
        @param token:  token
        @param timestamp: timestamp
        @param encrypt: encrypt text
        @param nonce: random string
        @return: signature
        """
        try:
            sortlist = [token, timestamp, nonce, encrypt]
            sortlist.sort()
            sha = hashlib.sha1()
            sha.update("".join(sortlist))
            return ierror.WXBizMsgCrypt_OK, sha.hexdigest()
        except Exception:
            return ierror.WXBizMsgCrypt_ComputeSignature_Error, None


class XMLParse:
    """get encrypt and generate a reply message"""

    # xml template
    AES_TEXT_RESPONSE_TEMPLATE = '''<xml>
    <Encrypt><![CDATA[%(msg_encrypt)s]]></Encrypt>
    <MsgSignature><![CDATA[%(msg_signaturet)s]]></MsgSignature>
    <TimeStamp>%(timestamp)s</TimeStamp>
    <Nonce><![CDATA[%(nonce)s]]></Nonce>
    </xml>'''

    def extract(self, xmltext):
        """ unpack encrypted message
        @param xmltext: xml text
        @return: encrypted message
        """
        try:
            xml_tree = ET.fromstring(xmltext)
            encrypt = xml_tree.find('Encrypt')
            touser_name = xml_tree.find('ToUserName')
            return ierror.WXBizMsgCrypt_OK, encrypt.text, touser_name.text
        except Exception:
            return ierror.WXBizMsgCrypt_ParseXml_Error, None, None

    def generate(self, encrypt, signature, timestamp, nonce):
        """Generate xml message
        @param encrypt: encrypted message text
        @param signature: signature
        @param timestamp: timestamp
        @param nonce: random string
        @return: xml text
        """
        resp_dict = {
            'msg_encrypt': encrypt,
            'msg_signaturet': signature,
            'timestamp': timestamp,
            'nonce': nonce,
        }
        resp_xml = self.AES_TEXT_RESPONSE_TEMPLATE % resp_dict
        return resp_xml


class PKCS7Encoder():
    """PKCS7-based encryption and decryption algorithm"""

    block_size = 32

    def encode(self, text):
        """
        @param text: orignial plaintext
        @return: remedium plaintext
        """
        text_length = len(text)
        # count remedium
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        # get remedium charector
        pad = chr(amount_to_pad)
        return text + pad * amount_to_pad

    def decode(self, decrypted):
        """Plaintext after you remove the decrypted
        @param decrypted: decrypted remedium plaintext
        @return: plaintext before remedium
        """
        pad = ord(decrypted[-1])
        if pad < 1 or pad > 32:
            pad = 0
        return decrypted[:-pad]


class Prpcrypt(object):
    """Receiving and Pushed to wechat encryption and decryption of messages"""

    def __init__(self, key):
        # self.key = base64.b64decode(key+"=")
        self.key = key
        # Set encryption mode AES.MODE_CBC
        self.mode = AES.MODE_CBC

    def encrypt(self, text, appid):
        """
        @param text: text need to be encrypt
        @return: encrypted text
        """
        # 16 random string added to the beginning of the plaintext
        struct_pack_text = struct.pack('I', socket.htonl(len(text)))
        text = self.get_random_str() + struct_pack_text + text + appid
        # Use custom stuffing plaintext
        pkcs7 = PKCS7Encoder()
        text = pkcs7.encode(text)
        # Encryption
        cryptor = AES.new(self.key, self.mode, self.key[:16])
        try:
            ciphertext = cryptor.encrypt(text)
            # using BASE64 string is encoded
            return ierror.WXBizMsgCrypt_OK, base64.b64encode(ciphertext)
        except Exception:
            return ierror.WXBizMsgCrypt_EncryptAES_Error, None

    def decrypt(self, text, appid):
        """delete remedium for decrypted plaintext
        @param text: Ciphertext
        @return: plaintext with out remedium
        """
        try:
            cryptor = AES.new(self.key, self.mode, self.key[:16])
            # using BASE64 decode and decrypt AES-CBC
            plain_text = cryptor.decrypt(base64.b64decode(text))
        except Exception:
            return ierror.WXBizMsgCrypt_DecryptAES_Error, None
        try:
            pad = ord(plain_text[-1])
            # Remove the remedium
            # pkcs7 = PKCS7Encoder()
            # plain_text = pkcs7.encode(plain_text)
            # remove 16 random char
            content = plain_text[16:-pad]
            xml_len = socket.ntohl(struct.unpack('I', content[:4])[0])
            xml_content = content[4:xml_len + 4]
            from_appid = content[xml_len + 4:]
        except Exception:
            return ierror.WXBizMsgCrypt_IllegalBuffer, None
        if from_appid != appid:
            return ierror.WXBizMsgCrypt_ValidateAppid_Error, None
        return 0, xml_content

    def get_random_str(self):
        """
        @return: random 16 charector string
        """
        rule = string.letters + string.digits
        str = random.sample(rule, 16)
        return "".join(str)


class WXBizMsgCrypt(object):
    # Constructor
    # @param sToken: developer token
    # @param sEncodingAESKey: developer EncodingAESKey
    # @param sAppId: developer AppId
    def __init__(self, sToken, sEncodingAESKey, sAppId):
        try:
            self.key = base64.b64decode(sEncodingAESKey + '=')
            assert len(self.key) == 32
        except Exception:
            throw_exception('[error]: EncodingAESKey invalid !')
            # return ierror.WXBizMsgCrypt_IllegalAesKey
        self.token = sToken
        self.appid = sAppId

    def EncryptMsg(self, sReplyMsg, sNonce, timestamp=None):
        # package encrypted reply message
        # @param sReplyMsg: reply message in xml
        # @param sTimeStamp: url args timestampe or custom made or None
        # @param sNonce: url args nonce or custom made
        # sEncryptMsg: encrypted 'msg_signature, timestamp, nonce, encrypt'
        # return: Success -> 0. sEncryptMsg, faild return 'None'
        pc = Prpcrypt(self.key)
        ret, encrypt = pc.encrypt(sReplyMsg, self.appid)
        if ret != 0:
            return ret, None
        if timestamp is None:
            timestamp = str(int(time.time()))
        # Generating secure signatures
        sha1 = SHA1()
        ret, signature = sha1.getSHA1(self.token, timestamp, sNonce, encrypt)
        if ret != 0:
            return ret, None
        xmlParse = XMLParse()
        return ret, xmlParse.generate(encrypt, signature, timestamp, sNonce)

    def DecryptMsg(self, sPostData, sMsgSignature, sTimeStamp, sNonce):
        # Test the authenticity of the message,
        # and obtain the decrypted plaintext.
        # @param sMsgSignature: signature, match url args msg_signature
        # @param sTimeStamp: timestamp, match url args timestamp
        # @param sNonce: random string, match url args nonce
        # @param sPostData: Ciphertext, match post request body
        # xml_content: Original decrypted while request return 0
        # @return: Success 0, failure to return the error code
        # Secure signature verification
        xmlParse = XMLParse()
        ret, encrypt, touser_name = xmlParse.extract(sPostData)
        if ret != 0:
            return ret, None
        sha1 = SHA1()
        ret, signature = sha1.getSHA1(self.token, sTimeStamp, sNonce, encrypt)
        if ret != 0:
            return ret, None
        if not signature == sMsgSignature:
            return ierror.WXBizMsgCrypt_ValidateSignature_Error, None
        pc = Prpcrypt(self.key)
        ret, xml_content = pc.decrypt(encrypt, self.appid)
        return ret, xml_content
