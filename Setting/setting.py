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

PROJECT_NAME = "Watch_Dogs-Server"
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
        global LOGGER_CONF_NAME, SETTING_JOSN_NAME, PROJECT_NAME
        self.log_init_done = False
        self.logger = None
        # 路径检测
        now_path = os.path.abspath('.')
        project_path = now_path[:now_path.rfind(PROJECT_NAME) + len(PROJECT_NAME)]
        setting_path = os.path.join(project_path, "Setting")
        # 配置文件读取
        self.log_conf_path = os.path.join(setting_path, LOGGER_CONF_NAME)
        self.setting_json_path = os.path.join(setting_path, SETTING_JOSN_NAME)
        if not os.path.exists(self.log_conf_path) or not os.path.exists(self.setting_json_path):
            print "配置文件读取异常 : 请检查", os.path.basename(sys.argv[0]).split(".")[
                0], ".py路径下是否有", LOGGER_CONF_NAME, SETTING_JOSN_NAME
            exit(-1)
        self.log_init()
        self.static_value_refresh()

    # Web
    PORT = 80
    # DB
    DB_HOST = ""
    DB_USER = ""
    DB_PORT = ""
    DB_PASSWORD = ""
    DB_CHARSET = ""
    DB_DATABASE_NAME = ""
    # encrypt
    KEY = ""
    # client
    CLIENT_DATA_FILE = ""
    PROCESS_INFO_INTERVAL_MIN = -1
    PROCESS_RECORD_CACHE_INTERVAL_MIN = -1
    PROCESS_RECORD_INTERVAL_MIN = -1
    HOST_INFO_INTERVAL_HOUR = -1
    HOST_RECORD_INTERVAL_MIN = -1

    # @staticmethod
    def static_value_refresh(self):
        """静态值初始化/刷新"""
        json_file = file(self.setting_json_path)
        setting = json.load(json_file)
        json_file.close()
        # 读取参数
        # Web
        Setting.PORT = setting["port"]
        # DB
        Setting.DB_HOST = setting["database"]["host"].encode("utf-8")
        Setting.DB_PORT = setting["database"]["port"]
        Setting.DB_USER = setting["database"]["user"].encode("utf-8")
        Setting.DB_PASSWORD = setting["database"]["password"].encode("utf-8")
        Setting.DB_CHARSET = setting["database"]["charset"].encode("utf-8")
        Setting.DB_DATABASE_NAME = setting["database"]["database_name"].encode("utf-8")
        # encrypt
        Setting.KEY = setting["key"].encode("utf-8")
        # client
        Setting.CLIENT_DATA_FILE = setting["client"]["client_data_file"].encode("utf-8")
        Setting.PROCESS_INFO_INTERVAL_MIN = setting["client"]["process_host_interval_min"]
        Setting.PROCESS_RECORD_CACHE_INTERVAL_MIN = setting["client"]["process_record_cache_interval_min"]
        Setting.PROCESS_RECORD_INTERVAL_MIN = setting["client"]["process_record_interval_min"]
        Setting.HOST_INFO_INTERVAL_HOUR = setting["client"]["host_info_interval_hour"]
        Setting.HOST_RECORD_INTERVAL_MIN = setting["client"]["host_record_interval_min"]

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
