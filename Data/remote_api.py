#!/usr/bin/env python
# encoding:utf8

"""
Watch_Dogs
远程监控客户端api调用
"""

import yaml
import time
import requests

from conf import setting

Setting = setting.Setting()
logger_client = Setting.logger


class Watch_Dogs_Client(object):
    """远程监控客户端"""

    def __init__(self, remote_host, remote_port=8000):
        """构造函数"""
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.apt_root = "http://" + remote_host + ":" + str(remote_port) + "/"
        self.watched_process_set = set([])

    def __str__(self):
        return "Watch_Dogs-Client @ " + self.remote_host + ":" + str(self.remote_port)

    def watch_process(self, pid):
        """添加监控进程"""
        self.watched_process_set.add(int(pid))
        r = self.get_api("/proc/watch/add/{}".format(pid))
        if type(r) == dict:
            logger_client.error("add not exist process" + str(pid))
            return r
        elif r is True:
            self.process_record_cache(pid)  # 初始化一次进程数据
            return True

    def is_process_watched(self, pid):
        if int(pid) in self.watched_process_set:
            r = self.get_api("/proc/watch/is/{}".format(int(pid)))
            if type(r) == dict:
                logger_client.error("is_process_watched error" + str(pid) + " -> " + str(r))
                return False
            elif r is True:
                return True
        else:
            return False

    def remove_watched_process(self, pid):
        if int(pid) in self.watched_process_set:
            self.watched_process_set.remove(int(pid))
            r = self.get_api("/proc/watch/remove/{}".format(int(pid)))
            if type(r) == dict:
                logger_client.error("remove_watched_process error" + str(pid) + " -> " + str(r))
                return False
            elif r is False:
                return True
        else:
            return False

    def get_api(self, url_path, payload=None, timeout=Setting.API_TIME_OUT):
        """调用远程api"""
        global logger_client
        request_addr = "http://" + self.remote_host + ":" + str(self.remote_port) + url_path
        try:
            r = requests.get(request_addr, params=payload, timeout=timeout)
        except requests.exceptions.ConnectTimeout as err:
            logger_client.error("time out : " + request_addr)
            return {"Error": "time out -" + request_addr}
        except requests.exceptions.ConnectionError as err:
            logger_client.error("connect error : " + request_addr)
            return {"Error": "connect error at " + request_addr}
        except Exception as err:
            logger_client.error("connect error : " + request_addr)
            return {"Error": "unexpected error at " + request_addr + " details : " + str(err)}
        return yaml.safe_load(r.text.encode("utf8"))

    def is_error_happen(self, res):
        """检查是否存在错误"""
        if isinstance(res, dict):
            if "Error" in res:
                return True
        return False

    # -----api-----
    def root(self):
        """/"""
        return self.get_api("/")

    # -----process-----
    def process_record_cache(self, pid):
        """进程数据"""
        return self.get_api("/proc/{}".format(str(pid)))

    def process_info(self, pid):
        """进程信息"""
        process_info = self.get_api("/proc/{}/info".format(str(pid)))
        return process_info

    # -----system-----
    def host_info(self):
        """远程主机信息"""
        host_info_data = {}
        # 收集主机数据
        try:
            host_root_data = self.root()  # 如果出现获取异常, 则不进行下面的数据获取
            if "Error" in host_root_data:
                return {"Error": "collect system info error (first) : " + str(host_root_data["Error"])}
            host_info_data.update(host_root_data)
            host_info_data.update(self.sys_info())
            host_info_data["CPU_info"] = self.sys_cpu_info()
            host_info_data["mem_KB"] = self.sys_mem_size()
            host_info_data.update(self.sys_net_ip())
            host_info_data["disk_stat"] = self.sys_disk_stat()
            host_info_data["default_net_device"] = self.sys_net_default_device()
        except Exception as err:
            logger_client.error("collect system info error : " + str(err))
            return {"Error": "collect system info error : " + str(err)}
        # 删除不必要的数据
        if "nethogs env" in host_info_data:
            host_info_data.pop("nethogs env")
        if "time" in host_info_data:
            host_info_data.pop("time")
        # 添加连接数据
        host_info_data["host"] = self.remote_host
        host_info_data["port"] = self.remote_port

        return host_info_data

    def host_record(self):
        """远程主机情况记录"""
        host_record_data = {}
        # 收集主机记录
        try:
            host_record_data["CPU"] = self.sys_cpu_percent()
            host_record_data["CPUs"] = self.sys_cpu_percents()
            host_record_data["mem"] = self.sys_mem_percent()
            host_record_data["read_MBs"], host_record_data["write_BMs"] = self.sys_io()
            host_record_data["net_upload_kbps"], host_record_data["net_download_kbps"] = self.sys_net()
            host_record_data.update(self.sys_loadavg())
            host_record_data.update(self.sys_uptime())
        except Exception as err:
            logger_client.error("collect system info error : " + str(err))
            return {"Error": "collect system info error : " + str(err)}
        # 添加连接数据
        host_record_data["host"] = self.remote_host

        return host_record_data

    def sys_info(self):
        return self.get_api("/sys/info")

    def sys_loadavg(self):
        return self.get_api("/sys/loadavg")

    def sys_uptime(self):
        return self.get_api("/sys/uptime")

    def sys_cpu_info(self):
        return self.get_api("/sys/cpu/info")

    def sys_cpu_percent(self):
        return self.get_api("/sys/cpu/percent")

    def sys_cpu_percents(self):
        return self.get_api("/sys/cpu/percents")

    def sys_mem_info(self):
        return self.get_api("/sys/mem/info")

    def sys_mem_size(self):
        return self.get_api("/sys/mem/size")

    def sys_mem_percent(self):
        return self.get_api("/sys/mem/percent")

    def sys_net_devices(self):
        return self.get_api("/sys/net/devices")

    def sys_net_default_device(self):
        return self.get_api("/sys/net/default_device")

    def sys_net_ip(self):
        return self.get_api("/sys/net/ip")

    def sys_net(self):
        return self.get_api("/sys/net")

    def sys_io(self):
        return self.get_api("/sys/io")

    def sys_disk_stat(self):
        return self.get_api("/sys/disk/stat")

    # -----log-----
    def get_log_exist(self, path):
        """检测日志文件是否存在"""
        payload = {"path": path}
        return self.get_api("/log/exist", payload=payload)

    def get_log_size(self, path):
        """获取日志文件大小"""
        payload = {"path": path}
        return self.get_api("/log/size", payload=payload)

    def get_log_head(self, path, n=100):
        """获取日志前n行"""
        payload = {"path": path, "n": n}
        return self.get_api("/log/head", payload=payload)

    def get_log_tail(self, path, n=100):
        """获取日志后n行"""
        payload = {"path": path, "n": n}
        return self.get_api("/log/tail", payload=payload)

    def get_log_last_update_time(self, path, n=100):
        """获取日志上次更新时间"""
        payload = {"path": path, "n": n}
        return self.get_api("/log/last_update_time", payload=payload)

    def get_keyword_lines(self, path, key_word):
        """搜索日志关键词"""
        payload = {"path": path, "key_word": key_word}
        return self.get_api("/log/keyword_lines", payload=payload)

    def get_keyword_lines_by_tail_n_line(self, path, key_word, n=100):
        """获取最后n行中包含关键词key_word的行"""
        payload = {"path": path, "n": n}
        return filter(lambda s: s.find(key_word) != -1, self.get_api("/log/tail", payload=payload))

    # -----manage-----
    # /proc/all_pid_name/
    def get_all_proc_with_name(self):
        """搜索日志关键词"""
        return self.get_api("/proc/all_pid_name/")

    # 有部分API功能尚未用到或改用SSH方式
    # 详见 : https://github.com/Watch-Dogs-HIT/Watch_Dogs-Client
