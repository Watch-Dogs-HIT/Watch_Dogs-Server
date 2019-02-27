#!/usr/bin/env python
# encoding:utf8

"""
Watch_Dogs
配置文件&日志
"""

import os
import sys
import json
import datetime
import logging
import logging.config

LOGGER_CONF_NAME = "logger.conf"
SETTING_JOSN_NAME = "setting.json"


class Setting(object):
    """静态配置"""

    # Singleton
    _instance = None

    def __new__(cls, *args, **kw):
        """单例模式"""
        if not cls._instance:
            cls._instance = super(Setting, cls).__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        global LOGGER_CONF_NAME, SETTING_JOSN_NAME
        self.log_init_done = False
        self.logger = None
        now_path = os.path.abspath('.')
        self.log_conf_path = os.path.join(now_path, LOGGER_CONF_NAME)
        self.setting_json_path = os.path.join(now_path, SETTING_JOSN_NAME)
        if not os.path.exists(self.log_conf_path) or not os.path.exists(self.setting_json_path):
            print "配置文件读取异常 : 请检查", os.path.basename(sys.argv[0]).split(".")[
                0], ".py路径下是否有", LOGGER_CONF_NAME, SETTING_JOSN_NAME
            exit(-1)
        self.log_init()
        self.static_value_refresh()

    PORT = 80

    # @staticmethod
    def static_value_refresh(self):
        """静态值初始化/刷新"""
        jsonFile = file(self.setting_json_path)
        setting = json.load(jsonFile)
        jsonFile.close()
        # 读取参数
        Setting.PORT = setting["port"]
        return setting

    def log_init(self):
        """对象出初始化"""
        # 只进行一次初始化
        if not self.log_init_done:
            self.log_init_done = True
            logging.config.fileConfig(self.log_conf_path)
            self.logger = logging.getLogger("main")
        return self.logger

    @staticmethod
    def get_local_time():
        """获取本地时间"""
        return str(datetime.datetime.now()).split(".")[0]

    @staticmethod
    def get_local_date():
        """获取本地日期"""
        return str(datetime.datetime.now()).split(" ")[0]
