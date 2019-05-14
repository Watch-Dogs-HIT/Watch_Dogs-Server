#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
基于SSH的远程主机控制、指令执行
"""

import time
import base64

import socket
import paramiko

from conf.setting import Setting

setting = Setting()
ssh_log = setting.logger


def remote_host_client(host, user, password, port):
    """连接远程客户端"""
    client = paramiko.SSHClient()  # 创建客户端
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host, port=port, username=user, password=password, timeout=3)
    except Exception as err:
        # ssh_log.warning("连接远程主机 " + user + " @ " + host + "出现问题 : " + str(err))
        print "连接远程主机 " + user + " @ " + host + "出现问题 : " + str(err)
        client.close()
        return None
    return client


def execute_command(host, user, password, port, commands=[]):
    """远程执行命令,获取结果"""
    res = {"status": "OK", "command_list": commands, "execute_command_result": []}
    client = remote_host_client(host, user, password, port)
    if client:
        for comm in commands:
            t = {"comm": comm, "stdout": None, "stderr": None, "status": "OK"}
            try:
                stdin, stdout, stderr = client.exec_command(comm)
                t["stdout"] = stdout.read()
                t["stderr"] = stderr.read()
                res["execute_command_result"].append(t)
            except Exception as err:
                res["status"] = "execute_error"
                res["error"] = str(err)
        client.close()
        return res
    else:
        res["status"] = "connect_error"
        return res


if __name__ == '__main__':
    res = execute_command("10.245.146.201", "root", "19950705", 22,
                          ["ls", "pwd", "ps ax", "touch test.py", "rm test.py"])
    for i in res["execute_command_result"]:
        print i["comm"]
        print "-------------"
        print i["stdout"]
