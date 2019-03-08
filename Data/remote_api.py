#!/usr/bin/env python
# encoding:utf8

"""
Watch_Dogs
远程监控客户端api调用
"""

import yaml
import time
import requests

from Setting import setting

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
        # todo - 根据远程内容来调用,返回 ? client 同样?

    def __str__(self):
        return "Watch_Dogs-Client @ " + self.remote_host + ":" + str(self.remote_port)

    def watch_process(self, pid):
        """添加监控进程"""
        self.watched_process_set.add(int(pid))
        r = self.get_api("/proc/watch/add/{}".format(pid))
        if type(r) == dict:
            logger_client.info("add not exist process" + str(pid))
            return r
        elif r is True:
            return True

    def is_process_watched(self, pid):
        pass

    def remove_watched_process(self, pid):
        pass

    def get_api(self, url_path, payload=None, timeout=2):
        """调用远程api"""
        global logger_client
        request_addr = "http://" + self.remote_host + ":" + str(self.remote_port) + url_path
        try:
            r = requests.get(request_addr, params=payload, timeout=timeout)
        except requests.exceptions.ConnectTimeout as err:
            logger_client.error("time out : " + request_addr)
            return {"Error": "time out -" + request_addr}

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
    def process_info(self, pid):
        """进程数据"""
        return self.get_api("/proc/{}".format(str(pid)))

    # -----system-----
    def host_info(self):
        """远程主机信息"""
        host = {}
        # 收集主机数据
        try:
            host.update(self.root())
            host.update(self.sys_info())
            host["CPU_info"] = self.sys_cpu_info()
            host["mem_KB"] = self.sys_mem_size()
            host.update(self.sys_net_ip())
            host["disk_stat"] = self.sys_disk_stat()
            host["default_net_device"] = self.sys_net_default_device()
        except Exception as err:
            logger_client.error("collect system info error : " + str(err))
            return {"Error": "collect system info error : " + str(err)}
        # 删除不必要的数据
        host.pop("nethogs env")
        host.pop("time")

        return host

    def host_record(self):
        """远程主机情况记录"""

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

    def sys_net_percent(self):
        return self.get_api("/sys/net/percent")

    def sys_disk_stat(self):
        return self.get_api("/sys/disk/stat")

    # -----func-----
    def get_log_head(self, path, n=100):
        """获取日志前n行"""
        payload = {"path": path, "n": n}
        return self.get_api("/log/head", payload=payload)


if __name__ == '__main__':
    c = Watch_Dogs_Client("118.126.104.182")
    c.host_info()
    # print c.host_info(15637)
    # print c.process_info(15637)
    # # print type(c.get_api("/proc/watch/add/15637"))
    # # 13859
