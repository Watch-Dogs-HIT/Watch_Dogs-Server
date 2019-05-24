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

    # PATH
    CONF_PATH = ""
    PROJECT_PATH = ""
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
    PROCESS_INFO_INTERVAL_MIN = -1
    PROCESS_RECORD_CACHE_INTERVAL_MIN = -1
    PROCESS_RECORD_INTERVAL_MIN = -1
    HOST_INFO_INTERVAL_HOUR = -1
    HOST_RECORD_INTERVAL_MIN = -1
    OLD_DATE_CLEAR_INTERVAL_DAY = -1
    API_TIME_OUT = -1
    SAVE_LAST_N_DAYS_DATA = -1
    REFRESH_CONF_HOUR = -1
    # email
    EMAIL_HOST = ""
    EMAIL_USER = ""
    EMAIL_PASS = ""
    EMAIL_SENDER = ""
    ALERT_INTERVAL_MIN = -1
    # client zip
    CLIENT_DOWNLOAD_LINK = ""
    CLIENT_FILE_ZIP = ""
    CLIENT_FILE_TAR = ""
    CLIENT_SCRIPT = ""

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
        setting_path = os.path.join(project_path, "conf")
        # 配置文件读取
        self.log_conf_path = os.path.join(setting_path, LOGGER_CONF_NAME)
        self.setting_json_path = os.path.join(setting_path, SETTING_JOSN_NAME)
        Setting.CONF_PATH = setting_path
        Setting.PROJECT_PATH = project_path
        if not os.path.exists(self.log_conf_path) or not os.path.exists(self.setting_json_path):
            print "配置文件读取异常 : 请检查", os.path.basename(sys.argv[0]).split(".")[
                0], ".py路径下是否有", LOGGER_CONF_NAME, SETTING_JOSN_NAME
            exit(-1)
        self.log_init()
        self.static_value_refresh()

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
        Setting.PROCESS_INFO_INTERVAL_MIN = setting["client"]["process_info_interval_min"]
        Setting.PROCESS_RECORD_CACHE_INTERVAL_MIN = setting["client"]["process_record_cache_interval_min"]
        Setting.PROCESS_RECORD_INTERVAL_MIN = setting["client"]["process_record_interval_min"]
        Setting.HOST_INFO_INTERVAL_HOUR = setting["client"]["host_info_interval_hour"]
        Setting.HOST_RECORD_INTERVAL_MIN = setting["client"]["host_record_interval_min"]
        Setting.OLD_DATE_CLEAR_INTERVAL_DAY = setting["client"]["old_date_clear_interval_day"]
        Setting.API_TIME_OUT = setting["client"]["api_timeout"]
        Setting.SAVE_LAST_N_DAYS_DATA = setting["client"]["save_last_n_days_data"]
        Setting.REFRESH_CONF_HOUR = setting["client"]["refresh_conf_hour"]
        # email
        Setting.EMAIL_HOST = setting["email"]["mail_host"]
        Setting.EMAIL_USER = setting["email"]["mail_user"]
        Setting.EMAIL_PASS = setting["email"]["mail_pass"]
        Setting.EMAIL_SENDER = setting["email"]["sender"]
        Setting.ALERT_INTERVAL_MIN = setting["email"]["alert_interval_min"]
        # client zip
        Setting.CLIENT_DOWNLOAD_LINK = setting["client_file"]["client_download_link"]
        Setting.CLIENT_FILE_ZIP = setting["client_file"]["client_file_zip"]
        Setting.CLIENT_FILE_TAR = setting["client_file"]["client_file_tar"]
        Setting.CLIENT_SCRIPT = setting["client_file"]["client_setup_script"]
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
