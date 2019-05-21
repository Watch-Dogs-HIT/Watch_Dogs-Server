#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
基于SSH的远程主机控制、指令执行
"""

import time

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
        ssh_log.warning("连接远程主机 " + user + " @ " + host + "出现问题 : " + str(err))
        print "连接远程主机 " + user + " @ " + host + "出现问题 : " + str(err)
        client.close()
        return None
    return client


def execute_command(host, user, password, port, commands=[], use_chan=False):
    """远程执行命令,获取结果"""
    res = {"status": "OK", "command_list": commands, "execute_command_result": []}
    client = remote_host_client(host, user, password, port)
    if client:
        if not use_chan:
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


def kill_process(host, user, password, port, pid=None, process_name=None):
    """关闭进程"""
    res = {"status": "OK", "kill_pid": pid, "kill_process_name": process_name, "result": "",
           "comm": "kill -9 {pid}".format(pid=pid),
           "stdout": None, "stderr": None, }
    client = remote_host_client(host, user, password, port)
    if client and pid:
        try:
            stdin, stdout, stderr = client.exec_command(res["comm"])
            res["stdout"] = stdout.read()
            res["stderr"] = stderr.read()
        except Exception as err:
            res["status"] = "execute_error"
            res["error"] = str(err)
        client.close()
        return res
    else:
        res["status"] = "connect_error"
        return res


def start_process(host, user, password, port, process_path=None, start_cmd=None):
    """远程执行命令,获取结果"""
    res = {"status": "OK", "process_path": process_path, "start_cmd": start_cmd}
    client = remote_host_client(host, user, password, port)
    if client:
        try:
            chan = client.invoke_shell()
            chan.send('cd {path}; {sc} \n'.format(path=process_path, sc=start_cmd))
            chan.recv(4096)
            time.sleep(1.3)
        except Exception as err:
            res["status"] = "execute_error"
            res["error"] = str(err)
        client.close()
        return res
    else:
        res["status"] = "connect_error"
        return res


if __name__ == '__main__':
    # Demo
    pass
    # res = start_process("10.245.146.201", "root", "19950705", 22, process_path="/home/houjie",
    #                    start_cmd="nohup python -u test.py &")
    print kill_process("10.245.146.202", "houjie", "19950705", 22, 22809)
