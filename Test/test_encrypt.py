#!/usr/bin/env python
# encoding:utf-8

import os
import unittest

from conf.encrypt import Prpcrypt


class TestPrpcrypt(unittest.TestCase):
    """AES加密解密测试"""

    def setUp(self):
        self.pc = Prpcrypt()
        self.test_message = "Watch_Dogs encrypt test"
        self.e = ""
        self.d = ""

    def test_encrypt(self):
        self.e = self.pc.encrypt(self.test_message)
        self.d = self.pc.decrypt(self.e)
        self.assertIsInstance(self.e, str)
        self.assertIsInstance(self.d, str)
        self.assertIs(self.d == self.test_message, True)
