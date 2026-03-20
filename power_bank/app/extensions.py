# -*- coding: utf-8 -*-
"""扩展：数据库连接池等，在 create_app 中初始化并挂到 app.extensions['db']。"""
import os
import threading
import sqlparse
import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB


class PowerMySQL:
    """数据库连接池，线程安全。通过 current_app.extensions['db'] 使用。"""

    def __init__(self, app=None):
        self.pool = None
        self._local = threading.local()
        self._sql_file_path = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """根据 app.config 初始化连接池。"""
        db_config = {
            'host': app.config.get('MYSQL_HOST', 'localhost'),
            'port': app.config.get('MYSQL_PORT', 3306),
            'user': app.config.get('MYSQL_USER', 'root'),
            'password': app.config.get('MYSQL_PASSWORD', ''),
            'database': app.config.get('MYSQL_DATABASE', 'power'),
            'autocommit': app.config.get('MYSQL_AUTOCOMMIT', True),
            'cursorclass': DictCursor,
        }
        self.pool = PooledDB(
            creator=pymysql,
            maxconnections=10,
            mincached=2,
            blocking=True,
            ping=7,
            **db_config
        )
        self._sql_file_path = app.config.get('SQL_FILE')
        app.extensions['db'] = self
        print("[OK] DB pool init: %s/%s" % (db_config['host'], db_config['database']))

    def execute(self, sql, params=None):
        """线程安全：从池中获取连接执行 SQL。"""
        conn = self.pool.connection()
        try:
            with conn.cursor() as cursor:
                affected_rows = cursor.execute(sql, params)
                if sql.strip().upper().startswith('SELECT'):
                    self._local.last_result = cursor.fetchall()
                else:
                    self._local.last_result = []
                return affected_rows
        except Exception as e:
            print(f"SQL执行失败: {e}")
            raise
        finally:
            conn.close()

    def fetchall(self):
        return getattr(self._local, 'last_result', [])

    def fetchone(self):
        res = self.fetchall()
        return res[0] if res else None

    def execute_sql_file(self, sql_path=None):
        """读取并执行 SQL 文件。"""
        target_sql = sql_path or self._sql_file_path
        if not target_sql or not os.path.exists(target_sql):
            print("[WARN] SQL file not found: %s" % target_sql)
            return
        with open(target_sql, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        for stmt in sqlparse.split(sql_content):
            stmt = stmt.strip()
            if stmt:
                self.execute(stmt)
        print("[OK] SQL file executed: %s" % os.path.basename(target_sql))

    def close(self):
        if self.pool:
            self.pool.close()
            print("[OK] DB pool closed.")


def get_db():
    """从当前 app 获取 DB 实例，供蓝图中使用。"""
    from flask import current_app
    return current_app.extensions['db']
