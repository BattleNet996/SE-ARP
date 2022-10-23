#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/3 12:40 下午
# @Author  : Wang Guoxin，Chen Wenjie, Tang Jiaxin

# 新增读取并执行sql文件的类方法exe_sql()，便于后续直接通过python配置mysql数据库
import crypt
import re
import mysql.connector
from pymysql.converters import escape_string
'''
对数据库进行增删改查
'''

class DBAction(object):
    #Todo 建议将数据库配置信息配置在yaml文件中。
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="wjj",
            database="apprepo"
        )
        print("successfully connected!")

    def close(self):
        self.db.close()

    def change_db(self,db_name):
        """更换数据库"""
        cursor = self.db.cursor()
        sql = "use {0}".format(db_name)
        cursor.execute(sql)
        cursor.close()
        self.db.commit()

    def exe_sql(self,path):
        """传入本地sql文件path，并执行"""
        cursor = self.db.cursor()
        try:
            with open(path, encoding='utf-8', mode='r') as f:
                # 读取整个sql文件，以分号切割。[:-1]删除最后一个元素，也就是空字符串
                sql_list = f.read().split(';')[:-1]
                for x in sql_list:
                    # 判断包含空行的
                    if '\n' in x:
                        # 替换空行为1个空格
                        x = x.replace('\n', ' ')

                    # 判断多个空格时
                    if '    ' in x:
                        # 替换为空
                        x = x.replace('    ', '')

                    # sql语句添加分号结尾
                    sql_item = x + ';'
                    # print(sql_item)
                    cursor.execute(sql_item)
                    print("执行成功sql: %s" % sql_item)
        except Exception as e:
            print(e)
            print('执行失败sql: %s' % sql_item)

        finally:
            # 关闭mysql连接
            cursor.close()
            self.db.commit()

    def insert_row_app_info(self,app_id, apk_name, package_name, version):
        cursor = self.db.cursor()
        sql = "INSERT INTO app_info (app_id, apk_name, package_name, version) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (app_id,apk_name, package_name, version))
        cursor.close()
        self.db.commit()

    def insert_row_state(self, app_id, state_id, activity_name, screen_shot, layout):
        cursor = self.db.cursor()
        sql = "INSERT INTO state (app_id, state_id, activity_name, screen_shot, layout) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (app_id, state_id, activity_name, screen_shot, layout))
        cursor.close()
        self.db.commit()

    def insert_row_transition(self, app_id, source_state, target_state, trigger_action, trigger_identifier, condition):
        cursor = self.db.cursor()
        sql = "INSERT INTO transition (app_id, source_state, target_state, trigger_action, trigger_identifier, conditions) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (app_id, source_state, target_state, trigger_action, trigger_identifier, condition))
        cursor.close()
        self.db.commit()

    def insert_row_scenarios(self, app_id, scenario_name, description, path):
        cursor = self.db.cursor()
        sql = "INSERT INTO scenarios (app_id, scenario_name, description, path) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (app_id, scenario_name, description, path))
        cursor.close()
        self.db.commit()

    def get_all_app_package_name(self):
        cursor = self.db.cursor()
        query = "SELECT package_name FROM app_info"
        cursor.execute(query)
        rows = list(cursor)
        package_name_list = []
        for row in rows:
            package_name_list.append(row[0])
        return package_name_list

    def get_app_id(self, package_name):
        cursor = self.db.cursor()
        query = "SELECT app_id FROM app_info WHERE package_name = %s"
        cursor.execute(query, (package_name,))
        rows = list(cursor)
        found_app_id = -1
        if len(rows) == 1:
            (found_app_id,) = rows[0]
        elif len(rows) > 1:
            print('ERROR: Multiple records.')
        else:
            print('ERROR: No matched record.')
        cursor.close()
        return found_app_id

    def get_app_info(self, package_name):
        """根据安装包名，读取app_info表，返回info表的所有APP信息，进行初始化"""
        cursor = self.db.cursor()
        query = "SELECT apk_name, package_name, version, author FROM app_info WHERE package_name = %s"
        cursor.execute(query, (package_name,))
        #获取所有记录表
        app_info_lst = cursor.fetchall()
        # for row in results:
        #     apk_name = row[0]
        #     package_name = row[1]
        #     version = row[2]
        #     author_id = row[3]
        # app_info_lst = [apk_name,package_name,version,author_id]
        cursor.close()
        return app_info_lst

    def get_state_by_id(self, state_id):
        cursor = self.db.cursor()
        query = "SELECT screen_shot, layout FROM state WHERE state_id = %s"
        cursor.execute(query, (state_id,))
        data = cursor.fetchall()
        return data[0][0], data[0][1]

    def get_state_list_by_app_id(self, app_id):
        cursor = self.db.cursor()
        query = "SELECT state_id, activity_name, screen_shot, layout FROM state WHERE app_id = %s"
        cursor.execute(query, (app_id,))
        data = cursor.fetchall()
        return data

    def get_transition_by_app_id(self, app_id):
        cursor = self.db.cursor()
        query = "SELECT source_state, target_state, trigger_action, trigger_identifier, conditions FROM transition WHERE app_id = %s"
        cursor.execute(query, (app_id,))
        data = cursor.fetchall()
        return data

    def get_scenarios_by_app_id(self, app_id):
        cursor = self.db.cursor()
        query = "SELECT scenario_name, description, path FROM scenarios WHERE app_id = %s"
        cursor.execute(query, (app_id,))
        data = cursor.fetchall()
        return data
    
    def create_user(self,uid,uname,upassword):
        """存储用户信息"""
        self.db.change_db('users')
        cursor = self.db.cursor()
        sql = "INSERT INTO user_info (uid, name, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (uid, uname, upassword))
        cursor.close()
        self.db.commit()

    def create_email(self,uid,email):
        """存入邮箱"""
        self.db.change_db('users')
        cursor = self.db.cursor()
        query = "INSERT INTO user_email (uid, email) VALUES (%s, %s)"
        cursor.execute(query, (uid, email,))
        cursor.close()
        self.db.commit()

    def register_check(self,uname):
        """用户注册时检查数据库中是否已存在该用户名，若是则返回失败"""
        self.db.change_db('users')
        cursor = self.db.cursor()
        query = "SELECT * FROM user_info WHERE name = %s"
        cursor.execute(query, (uname,))
        result = cursor.fetchall()
        if result:
            return False #查询到存在同名name，说明注册冲突，返回False
        else:
            return True #查询到未有同名name，说明可以注册，返回True

    def check_email_uid(self,uid):
        """使用uid验证邮箱表中是否已存用户邮箱"""
        self.db.change_db('users')
        cursor = self.db.cursor()
        query = "SELECT * FROM user_email WHERE uid = %s"
        cursor.execute(query, (uid,))
        result = cursor.fetchall()[0]
        return result

    def check_email_email(self, email):
        """使用email验证邮箱表中是否已存用户邮箱"""
        self.db.change_db('users')
        cursor = self.db.cursor()
        query = "SELECT * FROM user_email WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchall()[0]
        return result

    def get_uid(self):
        """获取用户表中的最大uid"""
        self.db.change_db('users')
        cursor = self.db.cursor()
        query = "SELECT MAX(uid) FROM user_info"
        cursor.execute(query,)
        maxuid = cursor.fetchall()[0]
        if maxuid:
            return maxuid + 1
        else:
            return 1

    def get_name_uid(self,uname):
        """获取用户名对应的uid"""
        self.db.change_db('users')
        cursor = self.db.cursor()
        query = "SELECT uid FROM user_info WHERE name = %s"
        cursor.execute(query, (uname,))
        uid = cursor.fetchall()[0]
        return uid

    def login_check(self,uname,upassword):
        """根据用户表单提交的用户名与用户密码，进行登录核验"""
        self.db.change_db('users')
        cursor = self.db.cursor()
        query = "SELECT password FROM user_info WHERE name = %s"
        cursor.execute(query, (uname,))
        password = cursor.fetchall()[0]
        if upassword == password:
            #("welcome {0} !".format(uname))
            return True
        else:
            #print("password wrong!")
            return False

    def upload_data(self,uid,app_name,time,file_path):
        """向文件数据库中添加记录，字段为用户ID、文件路径"""
        self.db.change_db('users')
        cursor = self.db.cursor()
        query = "INSERT INTO data_info(uid,app_name,time,file_path) values(%s,%s,%s,%s)"
        cursor.execute(query, (uid, app_name, time, file_path,))
        cursor.close()

    def delete_data(self,uid,file_path):
        """从文件数据库中删除记录，依据为用户ID和文件路径"""
        self.db.change_db('users')
        cursor = self.db.cursor()
        query = "DELETE FROM data_info where uid= %s AND file_path= %s"
        cursor.execute(query, (uid, file_path,))
        cursor.close()

    def select_data(self,uid):
        """从文件数据库中查找记录，依据为用户ID"""
        self.db.change_db('users')
        cursor = self.db.cursor()
        query = "SELECT * FROM data_info where uid= %s"
        cursor.execute(query, (uid,))
        result = cursor.fetchall()  # 它的返回值是多个元组,即返回多个行记录
        cursor.close()
        di = {}
        for uid,app_name,time,file_path in result:
            di[file_path] = [time, app_name]
        return di

'''
测试
if __name__ == "__main__":
    db = DBAction()
    print(db.get_app_id("com.forrestguice.suntimeswidget"))
    
'''
