#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
业务逻辑(SQL语句)
"""


# SQL语句生成及优化
class SQL(object):

    def __init__(self):
        self.note = "just 4 Watch_Dogs-Server"
        self.date = "2019.3"

    @staticmethod
    def insert_host_info(host, user, password):
        """创建主机记录"""
        return ("""INSERT INTO `Watch_Dogs`.`Host_info`(`host`, `user`, `password`) VALUES """
                """('{host}', '{user}', '{password}')""").format(
            host=host, user=user, password=password
        )

    @staticmethod
    def update_host_info(host_info):
        """更新主机信息"""
        # 去除单引号
        for k in host_info.keys():
            host_info[k] = str(host_info[k]).replace("'", "\\\'")

        return ("""UPDATE `Watch_Dogs`.`Host_info` SET """
                """`port` = {p}, """
                """`system` = '{s}', """
                """`kernel` = '{k}', """
                """`CPU_info` = '{C}', """
                """`mem_M` = {m}, """
                """`disk_stat` = '{ds}', """
                """`default_net_device` = '{dnd}', """
                """`intranet_ip` = '{i}', """
                """`extranet_ip` = '{e}' WHERE `host` = '{h}';""").format(
            p=host_info['port'], s=host_info['system'], k=host_info['kernel'], C=host_info['CPU_info'],
            m=host_info['mem_KB'], ds=host_info['disk_stat'], dnd=host_info['default_net_device'],
            i=host_info['intranet_ip'], e=host_info['extranet_ip'], h=host_info['host']
        )

    @staticmethod
    def insert_host_record(host_record):
        """插入主机记录"""
        # 去除单引号
        for k in host_record.keys():
            host_record[k] = str(host_record[k]).replace("'", "\\\'")

        return (
            """INSERT INTO `Watch_Dogs`.`Host_record`(`host`, `CPU`, `CPUs`, `mem`, `read_MBs`, """
            """`write_MBs`, `net_upload_kbps`, `net_download_kbps`, `lavg_1`, `lavg_5`, `lavg_15`, `nr`,`free_rate`, `uptime`) VALUES """
            """('{h}','{C}', '{Cs}', '{m}', '{r}', '{w}', '{nu}', '{nd}', '{l1}', '{l5}', '{l15}', '{nr}','{f}', '{up}') ;""").format(
            h=host_record['host'], C=host_record['CPU'], Cs=host_record['CPUs'], m=host_record['mem'],
            r=host_record['read_MBs'], w=host_record['write_BMs'], nu=host_record['net_upload_kbps'], nd=host_record['net_download_kbps'],
            l1=host_record['lavg_1'], l5=host_record['lavg_5'], l15=host_record['lavg_15'], nr=host_record['nr'],
            f=host_record['free rate'], up=host_record['system_uptime'],
        )


if __name__ == '__main__':
    # Demo
    print SQL.insert_host_info("118.126.104.182", "root", "0f3fc66c6c138324be707d110a39704c")
