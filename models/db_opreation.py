#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
数据库操作封装
"""

import pymysql
from warnings import filterwarnings
from conf.setting import Setting

db_setting = Setting()
log_db = db_setting.logger

filterwarnings('ignore', category=pymysql.Warning)  # 忽略警告


class DataBase:
    """MySQL数据库操作类"""

    def __init__(self):
        """数据库配置初始化"""
        global db_setting
        self.host = db_setting.DB_HOST
        self.port = db_setting.DB_PORT
        self.user = db_setting.DB_USER
        self.passwd = db_setting.DB_PASSWORD
        self.charset = db_setting.DB_CHARSET
        self.db_name = db_setting.DB_DATABASE_NAME
        # 链接对象
        self.conn = None
        self.cursor = None
        self.SSCursor = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 异常的 type、value 和 traceback
        if exc_val:
            log_db.error("DB Context Error:" + str(exc_val) + ":" + str(exc_tb))
        self.close()

    def connect(self, db_name=""):
        """连接数据库"""
        if db_name:
            db = db_name
        else:
            db = self.db_name
        try:
            self.conn = pymysql.Connection(
                host=self.host,
                port=self.port,
                user=self.user,
                passwd=self.passwd,
                charset=self.charset,
                db=db,
                use_unicode=False,
                connect_timeout=2880000,
            )
        except pymysql.Error, e:
            log_db.error('Connect Error:' + str(e))
        self.cursor = self.conn.cursor()
        self.SSCursor = self.conn.cursor(pymysql.cursors.SSCursor)
        if not self.cursor:
            raise (NameError, "Connect Failure")
        log_db.info("MySQL(" + str(self.host) + ") Connect Success")

    def close(self):
        """关闭数据库"""
        try:
            self.cursor.close()
            self.SSCursor.close()
            self.conn.close()
            log_db.info("MySQL(" + str(self.host) + ") Close")
        except pymysql.Error as e:
            log_db.error("Connect Error:" + str(e))

    def commit(self):
        """提交事务"""
        try:
            self.conn.commit()
            log_db.info("MySQL(" + str(self.host) + ") Commit")
        except pymysql.Error as e:
            log_db.error("Commit Error:" + str(e))

    def execute_sql_value(self, sql, value):
        """
        执行带values集的sql语句
        :param sql: sql语句
        :param value: 结果值
        """
        try:
            self.cursor.execute(sql, value)
        except pymysql.Error, e:
            if e.args[0] == 2013 or e.args[0] == 2006:  # 数据库连接出错，重连
                self.close()
                self.connect()
                self.commit()
                log_db.info("execute |sql(value) - time out,reconnect")
                self.cursor.execute(sql, value)
            else:
                log_db.error("execute |sql(value) - Error:" + str(e))
                log_db.error("SQL : " + sql)

    def execute_no_return(self, sql):
        """
        执行SQL语句,不获取查询结果,而获取执行语句的结果
        :param sql: SQL语句
        """
        try:
            return self.cursor.execute(sql)
        except pymysql.Error, e:
            if e.args[0] == 2013 or e.args[0] == 2006:  # 数据库连接出错，重连
                self.close()
                self.connect()
                self.commit()
                log_db.info("execute |sql(no result) - time out,reconnect")
                self.cursor.execute(sql)
            else:
                log_db.error("execute |sql(no result) - Error:" + str(e))
                log_db.error("SQL : " + sql)

    def execute(self, sql):
        """
        执行SQL语句
        :param sql: SQL语句
        :return: 获取SQL执行并取回的结果
        """
        res = None
        try:
            self.cursor.execute(sql)
            res = self.cursor.fetchall()
        except pymysql.Error, e:
            if e.args[0] == 2013 or e.args[0] == 2006:  # 数据库连接出错，重连
                self.close()
                self.connect()
                self.commit()
                log_db.error("execute |sql - time out,reconnect")
                log_db.error("execute |sql - Error 2006/2013 :" + str(e))
                log_db.error("sql = " + str(sql))
                res = self.execute(sql)  # 重新执行
            else:
                log_db.error("execute |sql - Error:" + str(e))
                log_db.error('SQL : ' + sql)
        return res

    def query_one(self, sql):
        """
        查询单条记录
        :param sql: SQL语句
        :return: 获取SQL执行并取回的结果
        """
        res = None
        try:
            self.cursor.execute(sql)
            res = self.cursor.fetchone()
        except pymysql.Error, e:
            if e.args[0] == 2013 or e.args[0] == 2006:  # 数据库连接出错，重连
                self.close()
                self.connect()
                self.commit()
                log_db.error("query_one |sql - time out,reconnect")
                log_db.error("query_one |sql - Error 2006/2013 :" + str(e))
                log_db.error("sql = " + str(sql))
                res = self.execute(sql)  # 重新执行
            else:
                log_db.error("query_one |sql - Error:" + str(e))
                log_db.error('SQL : ' + sql)
        return res

    def execute_Iterator(self, sql, pretchNum=1000):
        """
        执行SQL语句(转化为迭代器)
        :param sql: SQL语句
        :param pretchNum: 每次迭代数目
        :return: 迭代器
        """
        log_db.info('执行:' + sql)
        __iterator_count = 0
        __result = None
        __result_list = []
        try:
            Resultnum = self.cursor.execute(sql)
            for i in range(Resultnum):
                __result = self.cursor.fetchone()
                __result_list.append(__result)
                __iterator_count += 1
                if __iterator_count == pretchNum:
                    yield __result_list
                    __result_list = []
                    __iterator_count = 0
            yield __result_list  # 最后一次返回数据
        except pymysql.Error, e:
            log_db.error('execute_Iterator error:' + str(e))
            log_db.error('SQL : ' + sql)

    def execute_many(self, sql, params):
        """
        批量执行SQL语句
        :param sql: sql语句(含有%s)
        :param params: 对应的参数列表[(参数1,参数2..参数n)(参数1,参数2..参数n)...(参数1,参数2..参数n)]
        :return: affected_rows
        """
        affected_rows = 0
        try:
            self.cursor.executemany(sql, params)
            affected_rows = self.cursor.rowcount
        except pymysql.Error, e:
            if e.args[0] == 2013 or e.args[0] == 2006:  # 数据库连接出错，重连
                self.close()
                self.connect()
                self.commit()
                log_db.error("execute |sql - time out,reconnect")
                log_db.error("execute |sql - Error 2006/2013 :" + str(e))
                log_db.error("sql = " + str(sql))
                self.execute_many(sql, params)  # 重新执行
            else:
                log_db.error("execute many|sql - Error:" + str(e))
                log_db.error('SQL : ' + sql)
                return -1
        return affected_rows

    def execute_SScursor(self, sql):
        """使用pymysql SSCursor类实现逐条取回
        请不要使用此方法来进行增、删、改操作()
        最好在with[上下文管理器内使用]"""
        # sql不要带 ';'
        # 有可能会发生 2014, "Commands out of sync; you can't run this command now"
        # 详见 [MySQL-python: Commands out of sync](https://blog.xupeng.me/2012/03/13/mysql-python-commands-out-of-sync/)
        sql = sql.strip(';')
        # 只能执行单行语句
        if len(sql.split(';')) >= 2:
            return []
        try:
            self.SSCursor.execute(sql)
            return self.SSCursor
        except pymysql.Error, e:
            log_db.error("execute SScursor |sql - Error:" + str(e))
            log_db.error('SQL : ' + sql)
            return []


if __name__ == '__main__':
    # Demo
    with DataBase() as db:
        # Demo for execute
        # ------------------------------
        print db.execute("show tables")

        # Demo for execute_Iterator
        # ------------------------------
        for results in db.execute_Iterator("""SHOW TABLES;"""):
            for result in results:
                print result

        # Demo for execute_SScursor
        # ------------------------------
        for i in db.execute_SScursor("show tables;"):
            print i
