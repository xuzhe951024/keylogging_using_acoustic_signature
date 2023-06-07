# -*- coding: utf-8 -*-
# @Time    : 2021/5/29 下午5:47
# @Author  : ShaHeTop-Almighty-ares
# @Email   : yang6333yyx@126.com
# @File    : command_register.py
# @Software: PyCharm

import os
import click
import platform

from common.libs.db import project_db
from ExtendRegister.db_register import db

"""
export FLASK_APP=ApplicationExample.py
"""


def register_commands(app):
    """flask cli"""

    @app.cli.command("hello_world", help='hello-world')
    def  hello_world():
        print('hello world')

    @app.cli.command(help='首次进行ORM操作')
    def orm():

        ps = platform.system()
        if ps in ['Linux', 'Darwin']:
            os.system("rm -rf " + os.getcwd() + "/migrations")
        elif ps == 'Windows':
            os.system("rd " + os.getcwd() + "/migrations")
        else:
            print('未找到操作系统:'.format(ps))

        try:
            query_table_sql = """SHOW TABLES LIKE 'alembic_version';"""
            print(query_table_sql)
            query_result = project_db.execute_sql(sql=query_table_sql)
            print('query_result:{} {}'.format(query_result, bool(query_result)))
            if bool(query_result):
                delete_table_sql = """DROP TABLE alembic_version;"""
                print(delete_table_sql)
                delete_result = project_db.execute_sql(sql=delete_table_sql)
                print('delete_result:{} {}'.format(delete_result, bool(delete_result)))
            else:
                pass
        except BaseException as e:
            print('删除 alembic_version 失败:{}'.format(str(e)))

        try:
            os.system("flask db init")
            os.system("flask db migrate")
            os.system("flask db upgrade")
            print('创建成功')
        except BaseException as e:
            print('创建失败:{}'.format(str(e)))

    @app.cli.command(help='更新表')
    def table():
        try:
            os.system("flask db migrate")
            os.system("flask db upgrade")
            print('创建成功')
        except BaseException as e:
            print('创建失败:{}'.format(str(e)))
