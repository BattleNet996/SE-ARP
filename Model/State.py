'''

状态类，与数据库state表对应关系：
appId->app_id
stateId->state_id
activityName->activity_name
picture->screen_shot
layout->layout

由于picture存储为blob 二进制流，通过base64进行编码，因此需要用decoder进行解码，decoder即为此解码对象


author zhouxinyu

'''

import base64
import os
from os import path


class State:

    def __init__(self, id=-1):
        self.app_id = id
        self.state_id = -1
        self.activity_name = None
        self.picture = None
        self.layout = None

    def set_state_id(self, id):
        self.state_id = id

    def set_activity_name(self, ac):
        self.activity_name = ac

    def set_picture(self, ifstream):
        self.picture = ifstream

    def set_layout(self, l):
        self.layout = l

    def get_state_id(self):
        return self.state_id

    def get_activity_name(self):
        return self.activity_name

    def get_picture(self):
        return self.picture

    def get_layout(self):
        return self.layout

    # initPic()将数据转换为图片文件并保存
    def init_pic(self, out_path=None):
        b = base64.b64decode(self.picture)
        try:
            if out_path is None:
                '''pic_file = open('..\\..\\out\\' + str(self.state_id) + '.png','wb')
                pic_file.write(b)'''
                # 其他位置调用该模块时，../../out/寻址有问题
                # 修改为使用os.path寻址的方法
                curpath = path.dirname(__file__)
                parent_path = os.path.dirname(curpath)
                # papa_path = os.path.dirname(parent_path)
                # papa_path = os.path.dirname(papa_path)
                # papa_path = os.path.dirname(papa_path)
                # out_path = papa_path + "\\out\\"
                out_path = parent_path + "/out/"
            if not os.path.exists(out_path):
                os.makedirs(out_path)
            pic_file = open(out_path + str(self.state_id) + '.png', 'wb')
            pic_file.write(b)
        finally:
            pic_file.close()

    def __str__(self):
        return "[app_id:" + str(self.app_id) + " state_id:" + str(self.state_id) + " activity_name:" + str(
            self.activity_name) + " layout:" + str(self.layout) + "]"
