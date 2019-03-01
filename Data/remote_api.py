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

    def root(self):
        """/"""
        return self.get_api("/")

    def get_log_head(self, path, n=100):
        """获取日志前n行"""
        payload = {"path": path, "n": n}
        return self.get_api("/log/head", payload=payload)


if __name__ == '__main__':
    c = Watch_Dogs_Client("118.126.104.182")
    print c
    c.root()
    print c.watch_process(156372)
    print c.get_log_head("/home/ubuntu/Watch_Dogs/Watch_Dogs-Server/Data/remote_api.py")
    # print type(c.get_api("/proc/watch/add/15637"))
    # 13859
