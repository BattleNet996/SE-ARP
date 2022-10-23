'''

场景类，与数据库scenarios表项对应关系：
appId->app_id
scenarioName->scenario_name
description->description
path->path

author zhouxinyu

'''

import os


# Todo 将以下代码Scenario1改写到Scenario中
#我们模型合并用的是Scenario1代码，我们修改他。整合到标准呢的Scenario中。
'''
class Scenario1(object):
    def __init__(self, scenario_name, description, path):
        self.scenario_name = scenario_name
        self.description = description
        self.path = path.split('-')
        self.state_list = set(self.path)

    def get_line(self):
        return '[%s] [%s] [%s]' % (self.scenario_name, self.description, '-'.join(self.path))
'''

class Scenario:

    def __init__(self, id=-1):
        self.app_id = id
        self.scenario_name = None
        self.description = None
        self.path = None

    def set_name(self, n):
        self.scenario_name = n

    def set_des(self, d):
        self.description = d

    def set_path(self, p):
        self.path = p

    def get_name(self):
        return self.scenario_name

    def get_des(self):
        return self.description

    def get_path(self):
        return self.path

    def __str__(self):
        return "[app_id:" + str(self.app_id) + " scenario_name:" + str(self.scenario_name) + " description:" + str(
            self.description) + " path:" + str(self.path) + "]"