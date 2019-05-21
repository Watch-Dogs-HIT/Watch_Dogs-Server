#!/usr/bin/env python
# encoding:utf8

"""
Watch_Dogs
远程监控客户端管理
"""

import time

import schedule

from Data.remote_api import Watch_Dogs_Client
from conf import setting
from models.SQL_generate import SQL
from models.db_opreation import DataBase

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
        # db, monitor thread
        self.db = DataBase()
        self.monitor_thread = None
        # 读取数据结构
        self.read_remote_api_conf()
        logger_client_manage.info("ClientManager init OK, " + str(len(self.host_info_list)) + " host, " +
                                  str(len(self.process_info_list)) + " process")
        # 建立远程监控客户端
        for host_id, host_ip in self.host_info_list:
            self.connect_remote_api(host_id, host_ip)
        # 远程监控进程初始化
        for process_id, process_host, process_pid, process_cmd in self.process_info_list:
            self.ini_watched_process(process_id, process_host, process_pid, process_cmd)

    # init
    def read_remote_api_conf(self):
        """从数据库中读取远程监控数据"""
        with DataBase() as db:
            for host_info in db.execute(SQL.get_all_host()):
                self.host_info_list.append(map(str, host_info))
            for process_info in db.execute(SQL.get_all_process()):
                self.process_info_list.append(map(str, process_info))

    def update_remote_api_conf(self):
        """更新远程监控数据"""
        self.process_info_list = []
        self.host_info_list = []
        self.read_remote_api_conf()
        # 建立远程监控客户端
        for host_id, host_ip in self.host_info_list:
            self.connect_remote_api(host_id, host_ip)
        # 远程监控进程初始化
        for process_id, process_host, process_pid, process_cmd in self.process_info_list:
            self.ini_watched_process(process_id, process_host, process_pid, process_cmd)

    def connect_remote_api(self, host_id, host_ip, api_port=8000):
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
                        host_ip + " Watch_Dogs-Client connect ok, [nethogs env] : " + str(test_connect["nethogs env"]))
                    self.client[str(host_id)] = remote_api_client
                    return remote_api_client
            self.client[str(host_id)] = remote_api_client  # 为了健壮性,即使连接错误也创建远程管理对象并返回
            return remote_api_client
        else:
            return self.client[host_ip.strip()]

    def ini_watched_process(self, process_id, process_host, process_pid, process_cmd):
        """初始化监控进程"""
        wdc = self.client[process_host]
        res = wdc.watch_process(process_pid)
        if res is not True:
            logger_client_manage.error("Error : " + str(process_cmd) + "(" + str(process_pid) + ") @ " +
                                       str(process_host) + " watch process init failed")
        else:
            return True

    # host
    def update_host_info(self):
        """更新主机信息"""
        self.db.connect()
        for host_id, host_ip in self.host_info_list:
            wdc = self.client[str(host_id)]
            hi = wdc.host_info()
            if wdc.is_error_happen(hi):
                logger_client_manage.error("Error : " + str(host_ip) + " WDC host info get error")
                logger_client_manage.error("Error details: " + str(hi))
            else:
                logger_client_manage.info("update " + str(host_ip) + " system info")
                self.db.execute(SQL.update_host_info(hi))
            self.db.commit()
        self.db.commit()
        self.db.close()

    def insert_host_record(self):
        """插入主机状态记录"""
        self.db.connect()
        for host_id, host_ip in self.host_info_list:
            wdc = self.client[str(host_id)]
            hr = wdc.host_record()
            if wdc.is_error_happen(hr):
                logger_client_manage.error("Error : " + str(host_ip) + " WDC host record get error")
                logger_client_manage.error("Error details: " + str(hr))
                self.db.execute(SQL.update_host_info_error(host_id))  # 更新主机状态为异常
            else:
                logger_client_manage.info("insert " + str(host_ip) + " system record")
                self.db.execute(SQL.insert_host_record(host_id, hr))
            self.db.commit()
        self.db.commit()
        self.db.close()

    # process
    def update_process_info(self):
        """更新进程信息"""
        self.db.connect()
        for process_id, process_host_id, process_pid, process_cmd in self.process_info_list:
            wdc = self.client[str(process_host_id)]
            pi = wdc.process_info(process_pid)
            if wdc.is_error_happen(pi):
                if pi["Error"].find("process no longer exists") != -1:  # 进程崩溃
                    self.db.execute(SQL.update_process_info_not_exit(process_id))
                    logger_client_manage.error("Error : " + str(process_cmd) + "(" + str(process_pid) + ") @ no." +
                                               str(process_host_id) + " host process not exit!")
                else:  # other error
                    self.db.execute(SQL.update_process_info_error(process_id))
                    logger_client_manage.error("Error : " + str(process_cmd) + "(" + str(process_pid) + ") @ no." +
                                               str(process_host_id) + " host get process info fialed!")
                    logger_client_manage.error("Error details: " + str(pi))
                # TODO : 添加重新探测进程处理逻辑,利用 re_detect_process() 方法 重新获取现在的进程号,并更新记录
            else:
                logger_client_manage.info("update " + str(process_cmd) + "(" + str(process_pid) + ") @ no." +
                                          str(process_host_id) + " host process info")
                self.db.execute(SQL.update_process_info(process_id, pi))
            self.db.commit()
        self.db.commit()
        self.db.close()

    def insert_process_record(self):
        """插入进程状态数据"""
        self.db.connect()
        for process_id, process_host_id, process_pid, process_cmd in self.process_info_list:
            wdc = self.client[str(process_host_id)]
            pr = wdc.process_record_cache(process_pid)
            if wdc.is_error_happen(pr):
                if pr["Error"].find("process no longer exists"):  # 进程崩溃
                    logger_client_manage.error("Error : " + str(process_cmd) + "(" + str(process_pid) + ") @ no." +
                                               str(process_host_id) + " host process not exit.")
                else:  # other error
                    logger_client_manage.error("Error : " + str(process_cmd) + "(" + str(process_pid) + ") @ no." +
                                               str(process_host_id) + " host get process record fialed!")
                    logger_client_manage.error("Error details: " + str(pr))
                # TODO : 添加重新探测进程处理逻辑,同上...
            else:
                logger_client_manage.info("insert " + str(process_cmd) + "(" + str(process_pid) + ") @ no." +
                                          str(process_host_id) + " host process record cache")
                self.db.execute(SQL.insert_process_record(process_id, pr))
            self.db.commit()
        self.db.commit()
        self.db.close()

    def add_new_process(self, new_process_at_host_id, new_process_pid):
        """新添加的进程处理"""
        with DataBase() as db:
            # 获取 process_id
            new_process_pid = str(new_process_pid)
            new_process_at_host_id = str(new_process_at_host_id)
            new_process_id = -1
            for process_id, process_host_id, process_pid, process_cmd in self.process_info_list:
                if new_process_at_host_id == process_host_id and new_process_pid == process_pid:  # 找到新添加的进程
                    new_process_id = process_id
                    break
            # watch process
            wdc = self.client[str(new_process_at_host_id)]
            wdc.watch_process(new_process_pid)
            # process info
            pi = wdc.process_info(new_process_pid)
            if wdc.is_error_happen(pi):
                if pi["Error"].find("process no longer exists") != -1:  # 进程崩溃
                    db.execute(SQL.update_process_info_not_exit(new_process_id))
                else:  # other error
                    db.execute(SQL.update_process_info_error(new_process_id))
            else:
                print "process_info",
                db.execute(SQL.update_process_info_without_time(new_process_id, pi))
                print SQL.update_process_info_without_time(new_process_id, pi)
            db.commit()
            # process record
            pr = wdc.process_record_cache(new_process_pid)
            if wdc.is_error_happen(pr):
                db.execute(SQL.insert_process_record_error(new_process_id))
            else:
                db.execute(SQL.insert_process_record(new_process_id, pr))
            db.commit()

    def update_new_process(self, new_process_at_host_id, new_process_pid):
        """新添加的进程处理"""
        # 获取 process_id
        new_process_pid = str(new_process_pid)
        new_process_at_host_id = str(new_process_at_host_id)
        new_process_id = -1
        for process_id, process_host_id, process_pid, process_cmd in self.process_info_list:
            if new_process_at_host_id == process_host_id and new_process_pid == process_pid:  # 找到新添加的进程
                new_process_id = process_id
                break
        # watch process
        wdc = self.client[str(new_process_at_host_id)]
        wdc.watch_process(new_process_pid)
        # process info
        pi = wdc.process_info(new_process_pid)
        if wdc.is_error_happen(pi):
            if pi["Error"].find("process no longer exists") != -1:  # 进程崩溃
                sql1 = SQL.update_process_info_not_exit(new_process_id)
            else:  # other error
                sql1 = SQL.update_process_info_error(new_process_id)
        else:
            sql1 = SQL.update_process_info_without_time(new_process_id, pi)
        # process record
        pr = wdc.process_record_cache(new_process_pid)
        if wdc.is_error_happen(pr):
            sql2 = SQL.insert_process_record_error(new_process_id)
        else:
            sql2 = SQL.insert_process_record(new_process_id, pr)

        return sql1, sql2

    # log
    def log_status(self, host_id, path, n=100):
        """获取日志状态"""
        log_exist = self.client[str(host_id)].get_log_exist(path)
        if type(log_exist) == bool and log_exist:
            res = {"exist": True,
                   "last_update_time": self.client[str(host_id)].get_log_last_update_time(path),
                   "tail": self.client[str(host_id)].get_log_tail(path, n),
                   "size_KB": self.client[str(host_id)].get_log_size(path)
                   }
            for v in res.values():
                if type(v) == dict:
                    return {"error": "log func network error"}
            res["last_update_time"] = res["last_update_time"].strftime('%Y-%m-%d %H:%M:%S')
            return res
        elif type(log_exist) == dict:
            return log_exist  # 网络错误
        else:
            return {"exist": False}

    def log_search_keyword(self, host_id, path, key_word, n=1000):
        """在日志中搜索关键词"""
        res = self.client[str(host_id)].get_keyword_lines_by_tail_n_line(path, key_word, n)
        if type(res) == list:  # ok
            return {"search_result": self.client[str(host_id)].get_keyword_lines_by_tail_n_line(path, key_word, n)}
        else:  # network error
            return res

    # magpie
    def re_detect_process(self, prev_process_cmd):
        """重新探测进程"""
        # ...
        process_pid, process_cmd = "", ""
        return process_pid, process_cmd

    def clear_old_data(self, days=Setting.SAVE_LAST_N_DAYS_DATA):
        """清理一段时间内的数据"""
        self.db.connect()
        logger_client_manage.info("clear old data")
        self.db.execute(SQL.delete_old_host_record(days))
        self.db.execute(SQL.delete_old_process_record(days))
        # self.db.execute(SQL.delete_old_process_cache_record(days))
        self.db.commit()
        self.db.close()

    # manage
    def get_all_process(self, host_id):
        """获取该主机所有进程"""
        return self.client[str(host_id)].get_all_proc_with_name()

    # test
    def test_api(self):
        """测试api"""
        # 测试参数
        print "HOST_INFO_INTERVAL_HOUR", Setting.HOST_INFO_INTERVAL_HOUR
        print "HOST_RECORD_INTERVAL_MIN", Setting.HOST_RECORD_INTERVAL_MIN
        print "PROCESS_INFO_INTERVAL_MIN", Setting.PROCESS_INFO_INTERVAL_MIN
        # print "PROCESS_RECORD_CACHE_INTERVAL_MIN", Setting.PROCESS_RECORD_CACHE_INTERVAL_MIN
        print "PROCESS_RECORD_INTERVAL_MIN", Setting.PROCESS_RECORD_INTERVAL_MIN
        print "OLD_DATE_CLEAR_INTERVAL_DAY", Setting.OLD_DATE_CLEAR_INTERVAL_DAY
        # 测试功能
        self.update_host_info()
        self.insert_host_record()
        self.update_process_info()
        self.insert_process_record()
        # self.insert_process_record()
        self.clear_old_data()

    # work thread
    def manage_main_thread(self):
        """远程客户端管理主进程"""
        logger_client_manage.info("主机状态数据收集进程启动...")
        # host
        schedule.every(Setting.HOST_INFO_INTERVAL_HOUR).hours.do(self.update_host_info)
        schedule.every(Setting.HOST_RECORD_INTERVAL_MIN).minutes.do(self.insert_host_record)
        # process
        schedule.every(Setting.PROCESS_INFO_INTERVAL_MIN).minutes.do(self.update_process_info)
        schedule.every(Setting.PROCESS_RECORD_INTERVAL_MIN).minutes.do(self.insert_process_record)
        # schedule.every(Setting.PROCESS_RECORD_INTERVAL_MIN).minutes.do(self.insert_process_record)
        # clear
        schedule.every(Setting.OLD_DATE_CLEAR_INTERVAL_DAY).days.do(self.clear_old_data)
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    c = ClientManager()
    # c.add_new_process(2, 27098)
    # c.test_api()
    c.manage_main_thread()
