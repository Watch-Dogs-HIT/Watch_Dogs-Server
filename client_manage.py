#!/usr/bin/env python
# encoding:utf8

"""
Watch_Dogs
远程监控客户端管理
"""

import time
import schedule

from Setting import setting

from Database.SQL_generate import SQL
from Database.db_opreation import DataBase
from Data.remote_api import Watch_Dogs_Client

Setting = setting.Setting()
logger_client_manage = Setting.logger


class ClientManager(object):
    """监控客户端管理"""

    # Singleton
    _instance = None

    def __new__(cls, *args, **kw):
        """单例模式"""
        if not cls._instance:
            cls._instance = super(ClientManager, cls).__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        """构造函数"""
        # 初始化数据
        self.process_info_list = []  # (process_id,process_host,process_pid,process_cmd)
        self.host_info_list = []  # (host_id,host_ip)
        self.client = {}
        # 读取数据结构
        self.read_data_file()
        logger_client_manage.info("ClientManager init OK, " + str(len(self.host_info_list)) + " host, " +
                                  str(len(self.process_info_list)) + " process")
        # 建立远程监控客户端
        for host_id, host_ip in self.host_info_list:
            self.connect_remote_api(host_ip)
        # 远程监控进程初始化
        for process_id, process_host, process_pid, process_cmd in self.process_info_list:
            self.add_watch_process(process_id, process_host, process_pid, process_cmd)
        # 与数据库建立连接
        self.db = DataBase()
        self.db.db_connect()

    def __del__(self):
        """析构函数"""
        self.save_data_file()
        logger_client_manage.info("ClientManager del OK, " + str(len(self.host_info_list)) + " host, " +
                                  str(len(self.process_info_list)) + " process")

    def read_data_file(self):
        """读取监控数据文件"""
        with open(Setting.CLIENT_DATA_FILE, "r") as f:
            for line in f:
                if not line.startswith("#"):
                    if line.startswith("host;"):
                        self.host_info_list.append(line.strip().split(";")[1:])
                    elif line.startswith("process;"):
                        self.process_info_list.append(line.strip().split(";")[1:])

    def update_data_file(self, data_str):
        """更新监控数据文件"""
        with open(Setting.CLIENT_DATA_FILE, "a+") as f:
            f.write(data_str + "\n")

    def save_data_file(self):
        """保存当前的监控数据"""
        title = [
            "# ---------------------------------------",
            "# Watch_Dogs-Server 系统监视参数",
            "# host;主机id;主机ip",
            "# process;监控进程id;监控进程pid;监控进程cmd",
            "# ---------------------------------------"
        ]
        date = "# save date : " + Setting.get_local_time()
        with open(Setting.CLIENT_DATA_FILE, "w") as f:
            for line in title:
                f.write(line + "\n")
            f.write(date + "\n")
            for process_data in self.process_info_list:
                f.write("process;" + ";".join(process_data) + "\n")
            for host_data in self.host_info_list:
                f.write("host;" + ";".join(host_data) + "\n")

    def connect_remote_api(self, host_ip, api_port=8000):
        """连接到远程api客户端"""
        if host_ip.strip() not in self.client:
            remote_api_client = Watch_Dogs_Client(host_ip, remote_port=api_port)
            for i in xrange(3):  # 重试3次,成功即止
                test_connect = remote_api_client.root()
                if remote_api_client.is_error_happen(test_connect):
                    logger_client_manage.error("Error : " + str(host_ip) + ":" + str(api_port) + "connect error - "
                                               + test_connect["Error"])
                else:
                    logger_client_manage.info(
                        host_ip + "Watch_Dogs-Client connect ok, [nethogs env] : " + str(test_connect["nethogs env"]))
                    self.client[host_ip.strip()] = remote_api_client
                return remote_api_client
        else:
            return self.client[host_ip.strip()]

    def add_watch_process(self, process_id, process_host, process_pid, process_cmd):
        """添加监控进程数据"""
        self.process_info_list.append((process_id, process_host, process_pid, process_cmd))
        wdc = self.client[process_host.split(":")[0]]
        if wdc.watch_process(process_pid) is not True:
            logger_client_manage.error("Error : " + str(process_cmd) + "(" + str(process_pid) + ") @ " +
                                       str(process_host) + " watch process init failed")

    def add_watch_host(self, host_id, host_ip):
        """添加监控主机数据"""
        self.host_info_list.append((host_id, host_ip))

    def update_host_info(self):
        """更新主机信息"""
        for host_id, host_ip in self.host_info_list:
            wdc = self.client[host_ip]
            hi = wdc.host_info()
            if wdc.is_error_happen(hi):
                logger_client_manage.error("Error : " + str(host_ip) + " WDC host info get error")
                logger_client_manage.error("Error details: " + str(hi))
            else:
                logger_client_manage.info("update " + str(host_ip) + " system info")
                self.db.execute(SQL.update_host_info(hi))
        self.db.db_commit()

    def insert_host_record(self):
        """插入主机状态记录"""
        for host_id, host_ip in self.host_info_list:
            wdc = self.client[host_ip]
            hr = wdc.host_record()
            if wdc.is_error_happen(hr):
                logger_client_manage.error("Error : " + str(host_ip) + " WDC host record get error")
                logger_client_manage.error("Error details: " + str(hr))
            else:
                logger_client_manage.info("insert " + str(host_ip) + " system record")
                self.db.execute(SQL.insert_host_record(hr))
        self.db.db_commit()

    def update_process_info(self):
        """更新进程信息"""
        for process_id, process_host, process_pid, process_cmd in self.process_info_list:
            wdc = self.client[process_host.split(":")[0]]
            pi = wdc.process_info(process_pid)
            if wdc.is_error_happen(pi):
                if pi["Error"].find("process no longer exists") != -1:  # 进程崩溃
                    self.db.execute(SQL.update_process_info_allready_exit(process_id))
                    logger_client_manage.error("Error : " + str(process_cmd) + "(" + str(process_pid) + ") @ " +
                                               str(process_host) + " process exit!")
                else:  # other error
                    logger_client_manage.error("Error : " + str(process_cmd) + "(" + str(process_pid) + ") @ " +
                                               str(process_host) + " get process info fialed!")
                    logger_client_manage.error("Error details: " + str(pi))
                # todo : 添加重新探测进程处理逻辑,利用re_detect_process()方法
            else:
                logger_client_manage.info("insert " + str(process_cmd) + "(" + str(process_pid) + ") @ " +
                                          str(process_host) + " process info")
                self.db.execute(SQL.update_process_info(process_id, pi))
        self.db.db_commit()

    def cache_process_record(self):
        """插入进程状态数据"""
        for process_id, process_host, process_pid, process_cmd in self.process_info_list:
            wdc = self.client[process_host.split(":")[0]]
            pic = wdc.process_record_cache(process_pid)
            if wdc.is_error_happen(pic):
                if pic["Error"].find("process no longer exists"):  # 进程崩溃
                    logger_client_manage.error("Error : " + str(process_cmd) + "(" + str(process_pid) + ") @ " +
                                               str(process_host) + " process exit!")
                else:  # other error
                    logger_client_manage.error("Error : " + str(process_cmd) + "(" + str(process_pid) + ") @ " +
                                               str(process_host) + " get process record fialed!")
                    logger_client_manage.error("Error details: " + str(pic))
                # todo : 添加重新探测进程处理逻辑,利用re_detect_process()方法

            else:
                logger_client_manage.info("insert " + str(process_cmd) + "(" + str(process_pid) + ") @ " +
                                          str(process_host) + " process record")
                self.db.execute(SQL.insert_process_record_cache(process_id, pic))
        self.db.db_commit()

    def insert_process_record(self):
        """整理缓存的进程状态数据"""
        for process_id, _, _, _ in self.process_info_list:
            self.db.execute(SQL.process_cache2process_record(process_id))
            self.db.execute(SQL.delete_process_record_cache(process_id))
        self.db.db_commit()

    def re_detect_process(self, prev_process_cmd):
        """重新探测进程"""
        # ...
        process_pid, process_cmd = "", ""
        return process_pid, process_cmd

    def manage_main_thread(self):
        """远程客户端管理主进程"""
        logger_client_manage.info("主机状态数据收集进程启动...")
        # host
        schedule.every(Setting.HOST_INFO_INTERVAL_HOUR).hours.do(self.update_host_info)
        schedule.every(Setting.HOST_RECORD_INTERVAL_MIN).minutes.do(self.insert_host_record)
        # process
        schedule.every(Setting.PROCESS_INFO_INTERVAL_MIN).minutes.do(self.update_process_info)
        schedule.every(Setting.PROCESS_RECORD_CACHE_INTERVAL_MIN).minutes.do(self.cache_process_record)
        schedule.every(Setting.PROCESS_RECORD_INTERVAL_MIN).minutes.do(self.insert_process_record)

        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    c = ClientManager()
    c.manage_main_thread()
