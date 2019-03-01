#!/usr/bin/env python
# encoding:utf8

"""
Watch_Dogs
加解密工具函数
"""

from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

from setting import Setting

s = Setting()
KEY = s.KEY


class Prpcrypt(object):
    """加密与解密工具"""
    # Singleton
    _instance = None

    def __new__(cls, *args, **kw):
        """单例模式"""
        if not cls._instance:
            cls._instance = super(Prpcrypt, cls).__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self, key=""):
        global KEY
        if key:
            self.key = key
        else:
            self.key = KEY
        if len(self.key) % 16 != 0:
            print "Error : Key must be 16 bytes long"
        self.mode = AES.MODE_CBC

    def encrypt(self, text):
        """加密函数"""
        cryptor = AES.new(self.key, self.mode, self.key)
        # 密钥补足为16的位数
        count = len(text)
        add = 16 - (count % 16)
        text = text + ('\0' * add)
        # 加密
        self.ciphertext = cryptor.encrypt(text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

    def decrypt(self, text):
        """解密函数"""
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip('\0')