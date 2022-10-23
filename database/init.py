#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/24 0:50 下午
# @Author  : Chen Wenjie

'''
    用于初始化构建本地/云数据库
    新增了对用户数据库（内含用户信息表、数据存储表）的初始化与交互
'''

import mysql.connector
from api import DBAction
import api

def sourceData(source_sql_file_path):
    """从sql文件中读取数据并存入本地数据库"""
    db_name = input("select a database to exe data insert:") #输入要使用的数据库名
    db = DBAction()
    db.change_db(db_name)
    db.exe_sql(source_sql_file_path)

def initDatabase(init_sql_file_path):
    """初始化database"""
    db = DBAction()
    db.exe_sql(init_sql_file_path)

if __name__ == "__main__":

# 1.初始化原始数据库
#     print("__init_database__")
#     init_sql_path = "./sql/init_apprepo.sql"
#     initDatabase(init_sql_path)

# 2.初始化模型合并结果数据库
# print("__init_database__")
# init_sql_path = "./sql/init_merge.sql"
# initDatabase(init_sql_path)


# 3.读取本地数据
#     print("__source_data__")
#     source_sql_path = r'./sql/File_Manager_Pro_0.5_2021-02-09.sql'
#     sourceData(source_sql_path)

# 4.初始化用户数据库
    print("_init_database_users")
    initDatabase('./sql/init_users.sql')
    # pass

# 5.尝试插入用户登录数据
    uname = "wjj"
    upassword = "123"
    create_user(uname, upassword)

# 6.尝试核对用户登录信息
    uname = "wjj"
    upassword = "1234"
    login_check(uname, upassword)

# 7.尝试插入用户模型数据
    uid = 2
    file_path = "E:\\Desktop\\test"
    app_name = 'QQ'
    time  = '2021/5/31'
    upload_data(uid, app_name, time, file_path)
    
# 8.尝试读取用户模型数据
    uid = 2
    result = select_data(uid)