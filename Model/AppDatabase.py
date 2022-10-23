'''

按每个app为存储单元，把所有app按<app_id,app>键值对存入hashMap

author zhouxinyu

'''


class AppDatabase:

    def __init__(self):
        self.app_list = {}

    def set_app_list(self, apps):
        if self.app_list == None:
            self.app_list = {}
        self.app_list.update(apps)

    def get_app_list(self):
        return self.app_list

    def __str__(self):
        re = ''
        for key in self.app_list:
            re += str(self.app_list[key])
            re += '\n'
        return re