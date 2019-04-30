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

    # remote API

    @staticmethod
    def get_all_host():
        """获取所有主机"""
        return """SELECT `host_id`, `intranet_ip` FROM `Host_info`"""

    @staticmethod
    def get_all_process():
        """获取所有进程"""
        return """SELECT `process_id`, `host`, `pid`, `comm` FROM `Process`"""

    # User
    @staticmethod
    def select_status_by_uid(uid):
        """按uid查询用户权限"""
        return """SELECT `status` FROM `Watch_Dogs`.`User` WHERE `user_id` = '{i}';""".format(
            i=uid
        )

    @staticmethod
    def select_user_by_name(user):
        """按名称查询用户"""
        return """SELECT COUNT(*) FROM `Watch_Dogs`.`User` WHERE `user` = '{u}';""".format(
            u=user
        )

    @staticmethod
    def create_user(user, password_aes, email):
        """注册用户"""
        return """INSERT INTO `Watch_Dogs`.`User`(`user`, `password`, `email`) VALUES ("{u}", "{p}", "{e}") ;""".format(
            u=user, p=password_aes, e=email
        )

    @staticmethod
    def update_user_info(uid, update_field, update_value):
        """更新用户信息"""
        return """UPDATE `Watch_Dogs`.`User` SET `{f}` = '{v}' WHERE `user_id` = {uid}""".format(
            f=update_field, v=update_value, uid=uid
        )

    @staticmethod
    def update_user_login_time(uid):
        return """UPDATE `Watch_Dogs`.`User` SET `last_login_time` = now() WHERE `user_id` = %s""" % uid

    @staticmethod
    def check_login(user, password_aes):
        """验证登陆"""
        return """SELECT `user_id`, `user`, `status` FROM `Watch_Dogs`.`User` WHERE `user`='{u}' AND `password`='{p}' LIMIT 1""".format(
            u=user, p=password_aes
        )

    # Admin

    @staticmethod
    def show_all_user():
        """查看所有用户信息"""
        return """SELECT `user_id`, `user`, `brief`, `password`, `status`, `email` FROM `User`"""

    @staticmethod
    def get_user_watch_host_num(uid):
        """查看用户关注主机数量"""
        return """SELECT count(*) AS `host_num` FROM `User_Host` WHERE user_id = {uid}""".format(uid=uid)

    @staticmethod
    def get_user_watch_process_num(uid):
        """查看用户关注进程数量"""
        return """SELECT count(*) AS `process_num` FROM `User_Process` WHERE user_id = {uid}""".format(uid=uid)

    @staticmethod
    def update_user_status(new_status, uid):
        """更新用户状态"""
        return """UPDATE `Watch_Dogs`.`User` SET `status` = {ns} WHERE `user_id` = {uid}""".format(
            ns=new_status, uid=uid
        )

    # Client

    @staticmethod
    def insert_host_info(host, user, password):
        """创建主机记录"""
        return ("""INSERT INTO `Watch_Dogs`.`Host_info`(`host`, `user`, `password`) VALUES """
                """("{host}", "{user}", "{password}")""").format(
            host=host, user=user, password=password
        )

    @staticmethod
    def update_host_info_error(host_id):
        """更新主机信息(异常)"""
        return """UPDATE `Watch_Dogs`.`Host_info` SET `status` = 0 WHERE `host_id` = "{hid}" """.format(hid=host_id)

    @staticmethod
    def update_host_info(host_info):
        """更新主机信息"""

        return ("""UPDATE `Watch_Dogs`.`Host_info` SET """
                """`status` = 1,"""
                """`port` = {p}, """
                """`system` = "{s}", """
                """`kernel` = "{k}", """
                """`CPU_info` = "{C}", """
                """`mem_M` = {m}, """
                """`disk_stat` = "{ds}", """
                """`default_net_device` = "{dnd}", """
                """`intranet_ip` = "{i}", """
                """`extranet_ip` = "{e}" WHERE `host` = "{h}";""").format(
            p=host_info['port'], s=host_info['system'], k=host_info['kernel'], C=host_info['CPU_info'],
            m=host_info['mem_KB'], ds=host_info['disk_stat'], dnd=host_info['default_net_device'],
            i=host_info['intranet_ip'], e=host_info['extranet_ip'], h=host_info['host']
        )

    @staticmethod
    def insert_host_record(host_id, host_record):
        """插入主机记录"""

        return (
            """INSERT INTO `Watch_Dogs`.`Host_record`(`host_id`, `host`, `CPU`, `CPUs`, `mem`, `read_MBs`, """
            """`write_MBs`, `net_upload_kbps`, `net_download_kbps`, `lavg_1`, `lavg_5`, `lavg_15`, `nr`,`free_rate`, `uptime`) VALUES """
            """("{hi}", "{h}", "{C}", "{Cs}", "{m}", "{r}", "{w}", "{nu}", "{nd}", "{l1}", "{l5}", "{l15}", "{nr}","{f}", "{up}") ;""").format(
            hi=host_id, h=host_record['host'], C=host_record['CPU'], Cs=host_record['CPUs'], m=host_record['mem'],
            r=host_record['read_MBs'], w=host_record['write_BMs'], nu=host_record['net_upload_kbps'],
            nd=host_record['net_download_kbps'],
            l1=host_record['lavg_1'], l5=host_record['lavg_5'], l15=host_record['lavg_15'], nr=host_record['nr'],
            f=host_record['free rate'], up=host_record['system_uptime'],
        )

    @staticmethod
    def create_process_info(process_info):
        """新建进程信息"""

        return ("""INSERT INTO `Watch_Dogs`.`Process`(`host`, `pid`, `comm`, `cmdline`, `ppid`, `pgrp`, `state`,"""
                """ `thread_num`) VALUES ("{h}", {pid}, "{c}", "{cm}", {pp}, {pg}, "{s}", {t});""").format(
            h=process_info['host'], pid=process_info['pid'], c=process_info['comm'], cm=process_info['cmdline'],
            pp=process_info['ppid'], pg=process_info['pgrp'], s=process_info['state'], t=process_info['thread num']
        )

    @staticmethod
    def update_process_info(process_id, process_info):
        """更新进程信息"""

        return (
            """UPDATE `Watch_Dogs`.`Process` SET `process_id` = {id}, `host` = "{h}", `pid` = {pid}, `comm` = "{c}","""
            """`cmdline` = "{cm}", `ppid` = {pp}, `pgrp` = {pg}, `state` =  "{s}", `thread_num` = {t}, `update_time` = now() """
            """WHERE `process_id` = {id} ;""").format(
            id=process_id, h=process_info['host'], pid=process_info['pid'], c=process_info['comm'],
            cm=process_info['cmdline'], pp=process_info['ppid'], pg=process_info['pgrp'], s=process_info['state'],
            t=process_info['thread num']
        )

    @staticmethod
    def update_process_info_error(process_id):
        """更新进程信息(错误)"""

        return ("""UPDATE `Watch_Dogs`.`Process` SET `state` =  "0" WHERE `process_id` = {id} ;""").format(
            id=process_id)

    @staticmethod
    def update_process_info_not_exit(process_id):
        """更新进程信息(不存在)"""

        return ("""UPDATE `Watch_Dogs`.`Process` SET `state` =  "X" WHERE `process_id` = {id} ;""").format(
            id=process_id)

    @staticmethod
    def insert_process_record(process_id, process_record):
        """插入进程记录"""
        # 去除单引号
        return ("""INSERT INTO `Watch_Dogs`.`Process_record`(`process_id`, `cpu`, `mem`, `read_MBs`,"""
                """`write_MBs`, `net_upload_kbps`, `net_download_kbps`) VALUES ("""
                """{id}, {c}, {m}, {r}, {w}, {u}, {d})""").format(
            id=process_id, c=process_record['cpu'], m=process_record['mem'],
            r=process_record['io'][0], w=process_record['io'][1],
            u=process_record['net_recent'][0], d=process_record['net_recent'][1]
        )

    @staticmethod
    def delete_old_host_record(days=7):
        """删除days天数之前的主机状态数据"""
        return ("""DELETE FROM `Host_record` WHERE `record_id` in (SELECT t.record_id FROM("""
                """SELECT `record_id` FROM `Host_record` WHERE DAY(now()) - DAY(`record_time`)  > {d}) AS t);""").format(
            d=days
        )

    @staticmethod
    def delete_old_process_record(days=7):
        """删除days天数之前的进程状态数据"""
        return ("""DELETE FROM `Process_record` WHERE `record_id` in (SELECT t.record_id FROM("""
                """SELECT `record_id` FROM `Process_record` WHERE DAY(now()) - DAY(`record_time`)  > {d}) AS t);""").format(
            d=days
        )

    # Index

    @staticmethod
    def get_user_watch_process(uid):
        """查看用户关注进程信息"""
        return ("""SELECT `host`, `process_id`, `pid`, `comm`, `state`  FROM `Process` WHERE `process_id` IN """
                """(SELECT `process_id` FROM `User_Process` WHERE user_id = {uid})""").format(uid=uid)

    @staticmethod
    def get_user_watch_host(uid):
        """查看用户关注主机信息"""
        return ("""SELECT `host_id`, `status` FROM `Host_info` WHERE `host_id` IN """
                """(SELECT `host_id` FROM `User_Host` WHERE user_id = {uid})""").format(uid=uid)

    @staticmethod
    def get_host_recent_record(host_id):
        """获取主机最近一条记录"""
        return """SELECT * FROM `Host_record` WHERE host_id = {hid} ORDER BY record_time DESC LIMIT 1""".format(
            hid=host_id
        )

    @staticmethod
    def get_user_all_host_relation(user_id):
        """获取主机与用户关系"""
        return """SELECT relation_id, host_id, `comment`, `type` FROM `User_Host` WHERE user_id = {uid} """.format(
            uid=user_id
        )

    @staticmethod
    def get_user_host_relation(user_id, host_id):
        """获取主机与用户关系"""
        return """SELECT relation_id, `comment`, `type` FROM `User_Host` WHERE user_id = {uid} AND host_id = {hid}""".format(
            hid=host_id, uid=user_id
        )

    @staticmethod
    def get_process_info(process_id):
        """获取进程最近一条记录"""
        return """SELECT * FROM `Process` WHERE process_id = {pid}""".format(
            pid=process_id
        )

    @staticmethod
    def get_process_recent_record(process_id):
        """获取进程最近一条记录"""
        return """SELECT * FROM `Process_record` WHERE process_id = {pid} ORDER BY record_time DESC LIMIT 1""".format(
            pid=process_id
        )

    @staticmethod
    def get_user_process_relation(user_id, process_id):
        """获取进程与用户关系"""
        return """SELECT relation_id, host_id, `type`, `comment`, process_id FROM `User_Process` WHERE user_id = {uid} AND process_id = {pid}""".format(
            pid=process_id, uid=user_id
        )

    # Host
    @staticmethod
    def get_host_id(host):
        """获取主机id"""
        return """SELECT `host_id` FROM `Host_info` WHERE `host` = '{h}'""".format(h=host)

    @staticmethod
    def check_host_watched(host):
        """确认主机是否被监控"""
        return """SELECT count(*) AS `host_exist` FROM `Host_info` WHERE `host` = '{h}'""".format(h=host)

    @staticmethod
    def get_host_info(hid):
        """获取主机信息"""
        return """SELECT * FROM Host_info WHERE `host_id` = {h}""".format(h=hid)

    @staticmethod
    def get_host_records(hid, num=20):
        """获取主机资源记录"""
        return """SELECT * FROM Host_record WHERE `host_id` = {h} ORDER BY `record_time` DESC LIMIT {n}""".format(
            h=hid, n=num
        )

    @staticmethod
    def delete_user_host_relation(uid, hid):
        """删除主机与用户关系"""
        return """DELETE FROM `Watch_Dogs`.`User_Host` WHERE `user_id` = {u} AND `host_id` = {h}""".format(
            u=uid, h=hid
        )

    # Process

    @staticmethod
    def check_process_watched(host, pid):
        """确认进程是否被监控"""
        return """SELECT count(*) AS `process_exist` FROM Process WHERE `host` = '{h}' AND `pid` = {p}""".format(
            h=host, p=pid)

    @staticmethod
    def get_process_id(host, pid):
        """获取进程id"""
        return """SELECT `process_id` FROM Process WHERE `host` = '{h}' AND `pid` = {p}""".format(
            h=host, p=pid)

    @staticmethod
    def add_watch_process(host, pid):
        """添加进程"""
        return """INSERT INTO `Watch_Dogs`.`Process`(`host`, `pid`) VALUES ('{h}', {p})""".format(
            h=host, p=pid
        )

    @staticmethod
    def get_insert_id_in_process():
        """获取最新插入数据的自增id"""
        return """INSERT INTO `Watch_Dogs`.`Process`(`host`, `pid`) VALUES ('1', 2)"""

    @staticmethod
    def add_user_process_relation(uid, hid, pid, com, c_type):
        """添加用户进程关系"""
        return ("""INSERT INTO `Watch_Dogs`.`User_Process`(`user_id`, `host_id`, `process_id`, `comment`, `type`) """
                """VALUES ({u}, {h}, {p}, '{c}', '{t}')""").format(u=uid, h=hid, p=pid, c=com, t=c_type)

    @staticmethod
    def get_user_process_relation_id(uid, hid, pid):
        """获取用户-进程关系id"""
        return """SELECT `relation_id` FROM User_Process WHERE `user_id` = {u} AND `host_id` = {h} AND `process_id` = {p}""".format(
            u=uid, p=pid, h=hid
        )

    @staticmethod
    def get_process_record(pid):
        """获取进程状态"""
        return """SELECT * FROM `Process` WHERE process_id = {p}""".format(p=pid)

    @staticmethod
    def get_process_records(pid, num):
        """获取进程资源记录"""
        return """SELECT * FROM Process_record WHERE `process_id` = {p} ORDER BY `record_time` DESC LIMIT {n}""".format(
            p=pid, n=num
        )


if __name__ == '__main__':
    # Demo
    print SQL.process_cache2process_record(1)
    print SQL.create_user("root", "0f3fc66c6c138324be707d110a39704c")
    print SQL.create_user("houjie", "0f3fc66c6c138324be707d110a39704c")
    print SQL.check_login("houjie", "0f3fc66c6c138324be707d110a39704c")
    print SQL.update_user_login_time(1)
