#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
数据库异步操作封装
"""

import tormysql
from tornado import gen

from Setting.setting import Setting

db_setting = Setting()
log_db = db_setting.logger


# note : tormysql 和 tornadoredis 一定要结合tornado来使用

class AsyncDataBase(object):
    """基于tormysql的MySQL异步操作封装"""

    # Singleton
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(AsyncDataBase, cls).__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        global db_setting
        self.host = db_setting.DB_HOST
        self.port = db_setting.DB_PORT
        self.user = db_setting.DB_USER
        self.password = db_setting.DB_PASSWORD
        self.charset = db_setting.DB_CHARSET
        self.db_name = db_setting.DB_DATABASE_NAME
        self.pool = tormysql.ConnectionPool(
            max_connections=20,  # max open connections
            idle_seconds=7200,  # conntion idle timeout time, 0 is not timeout
            wait_connection_timeout=3,  # wait connection timeout
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.password,
            db=self.db_name,
            charset=self.charset
        )

    @gen.coroutine
    def query(self, sql, args=None):
        """查询所有结果"""
        res = None
        with (yield self.pool.Connection()) as conn:
            try:
                with conn.cursor(cursor_cls=tormysql.DictCursor) as cursor:
                    yield cursor.execute(sql, args)
                    res = cursor.fetchall()
            except Exception, e:
                log_db.error("(tormysql) query :" + str(e.args))
            else:
                yield conn.commit()
        raise gen.Return(res)

    @gen.coroutine
    def query_one(self, sql, args=None):
        """单查询"""
        data = None
        with (yield self.pool.Connection()) as conn:
            try:
                with conn.cursor(cursor_cls=tormysql.DictCursor) as cursor:
                    yield cursor.execute(sql, args)
                    data = cursor.fetchone()
            except Exception, e:
                log_db.error("(tormysql) query one :" + str(e.args))
            else:
                yield conn.commit()

        raise gen.Return(data)

    @gen.coroutine
    def execute(self, sql):
        """执行"""
        ret = None
        with (yield self.pool.Connection()) as conn:
            try:
                with conn.cursor(cursor_cls=tormysql.DictCursor) as cursor:
                    ret = yield cursor.execute(sql)
            except Exception, e:
                log_db.error("(tormysql) execute :" + str(e.args))
                yield conn.rollback()
            else:
                yield conn.commit()
        raise gen.Return(ret)

    @gen.coroutine
    def execute_many(self, sql, args=None):
        """批量执行"""
        ret = None
        with (yield self.pool.Connection()) as conn:
            try:
                with conn.cursor(cursor_cls=tormysql.DictCursor) as cursor:
                    ret = yield cursor.executemany(sql, args)
            except Exception, e:
                log_db.error("(tormysql) execute many :" + str(e.args))
                yield conn.rollback()
            else:
                yield conn.commit()
        raise gen.Return(ret)


if __name__ == '__main__':
    # Demo
    db = AsyncDataBase()


    @gen.coroutine
    def test_connect(test_sql="show tables"):
        res = yield db.query(test_sql)
        raise gen.Return(res)  # 通过 raise gen.Return(res) 返回数据


    @gen.coroutine
    def get_result():
        res = yield test_connect()  # 通过yield接收数据,并且外层函数需要添加gen.coroutine装饰器
        print res


    @gen.coroutine
    def test_execute():
        yield db.execute("""truncate Test""")
        res = yield db.execute("""INSERT INTO Test(test) VALUES ('0')""")
        print res


    @gen.coroutine
    def test_execute_many():
        res = yield db.execute_many("""INSERT INTO Test(test) VALUES (%s)""",
                                    [('1'), ('2'), ('3'), ('4')]
                                    )
        print res


    @gen.coroutine
    def test_query():
        res = yield db.query("""SELECT * FROM Test""")
        print res


    @gen.coroutine
    def test_query_one():
        res = yield db.query_one("""SELECT * FROM Test""")
        print res


    # test
    from tornado.ioloop import IOLoop

    IOLoop.current().run_sync(get_result)
    IOLoop.current().run_sync(test_execute)
    IOLoop.current().run_sync(test_execute_many)
    IOLoop.current().run_sync(test_query)
    IOLoop.current().run_sync(test_query_one)
