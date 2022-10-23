#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2021/6/2 14:20 下午
# @Author  : Wang Zhixing，Wang Guoxin，Tang Jiaxin，Chen Wenjie
# 1、创建Model
# 2、保存Model到output文件夹中。
# 3、保存Model到database中

import sys
sys.path.append('..')
from App import App
from Transition import Transition
import os
from database.api import DBAction
from State import State
from util.read_file import *
from Scenario import Scenario
from Event import Event
import pandas as pd
import json
import shutil


class Model(App):
    def __init__(self):
        super(Model, self).__init__(id=-1, apk=None, pck=None, v=None)
        self.transitions = []
        self.state_list = []
        self.trans_df = None
    '''
    App类：
        app基础信息：
            app_id：app的id
            apk_name：app的安装包的名称
            package_name：app的包名
            apk_version：app的安装包的版本号
        app状态信息：
            states(dict)：整个app所有的state_id到state的索引表
                元素类型：State
            scenarios：app的场景列表
    Model类：
        transitions(list)：模型的跳转信息表
            元素类型：Transition
        state_list(list)：模型涉及到的app的状态列表
            元素类型：State
        用于合并的数据结构：
            trans_df(DataFrame)：存储source_id，target_id，trigger_action和trigger_identifier组合的表格
        app_running_path
    '''

    def Build_Model_From_Project(self, project_path):
        # 从文件中读取Model
        apk_name, package_name, version, author_id = read_app_info(project_path)  # 从文件中读取app信息
        self.apk_name = apk_name
        self.apk_version = version
        self.package_name = package_name
        states = read_state_info(project_path)  # 读取模型涉及到的app状态列表
        for (state_id, activity_name, binary_data, layout) in states:
            state = State(self.app_id)
            state.set_state_id(int(state_id))
            state.set_activity_name(activity_name)
            state.set_picture(binary_data)
            state.set_layout(layout)
            # file_path = f"./Data/2021Se/screens/{state_id}.uix"
            # with open(file_path, 'w') as f:     # 把layout写成uix文件
                # f.write(layout)
            # new_state.set_layout(file_path)
            self.state_list.append(state)  # 存入state_list

        transitions = read_transitions(project_path)  # 读取模型的app跳转信息集合
        transition_id = 0
        for transition_info in transitions:
            if len(transition_info) == 3:
                source_state, target_state, trigger_action = int(transition_info[0]), int(transition_info[1]), \
                                                             transition_info[2]
                transition = Transition(self.app_id)
                transition.set_source_id(self.state_list[source_state].state_id)
                transition.set_target_id(self.state_list[target_state].state_id)
                transition.set_transition_id(transition_id)
                event = Event(trigger_action, '', '')
                transition.set_event(event)
                self.transitions.append(transition)  # 转换为Transition类型，并存入transitions
            else:  # len(transition_info) == 4
                source_state, target_state, trigger_action, trigger_identifier = int(transition_info[0]), int(
                    transition_info[1]), transition_info[2], transition_info[3]
                transition = Transition(self.app_id)
                transition.set_source_id(self.state_list[source_state].state_id)
                transition.set_target_id(self.state_list[target_state].state_id)
                transition.set_transition_id(transition_id)
                event = Event(trigger_action, trigger_identifier, '')
                transition.set_event(event)
                self.transitions.append(transition)  # 转换为Transition类型，并存入transitions
            transition_id += 1

        scenarios = read_scenarios_info(project_path)
        for scenario in scenarios:
            scenario_name = scenario[0]
            desc = scenario[1]
            path = scenario[2]
            new_scenarios = Scenario(self.app_id)
            new_scenarios.set_name(scenario_name)
            new_scenarios.set_des(desc)
            new_scenarios.set_path(path)
            self.scenarios.append(new_scenarios)

    def Build_Model_From_Database(self, package_name):
        """修改/增添了从数据库中读取Model的API"""

        self.package_name = package_name
        db = DBAction()
        db.change_db("apprepo")

        app_id = db.get_app_id(self.package_name)
        if app_id == -1:
            return

        self.app_id = app_id  # 将数据库的app_id传给本Model
        # apk_name, package_name, version, author_id = db.get_app_info(package_name)  # 从数据库中读取app信息

        app_info_list = db.get_app_info(package_name)  # 从数据库中读取app信息
        self.apk_name = app_info_list[0][0]
        self.apk_version = app_info_list[0][2]
        self.package_name = app_info_list[0][1]
        author_id = app_info_list[0][3]

        state_data = db.get_state_list_by_app_id(app_id)  # 读取模型涉及到的app状态列表
        for data in state_data:
            state_id, activity_name, screen_shot, layout = data[0], data[1], data[2], data[3]
            new_state = State(self.app_id)
            new_state.set_state_id(int(state_id))
            new_state.set_activity_name(activity_name)
            new_state.set_picture(screen_shot)
            new_state.init_pic('./Data/2021Se/screens')
            new_state.set_layout(os.path.join('./Data/2021Se', 'screens', str(state_id) + '.uix'))
            # new_state.set_layout(os.path.join('..Data', 'screens', str(state_id) + '.uix'))  # 不确定！
            self.state_list.append(new_state)  # 转换为State类型，并存入state_list

        transition_data = db.get_transition_by_app_id(app_id)  # 读取模型的app跳转信息集合
        transition_id = 0
        for transition_info in transition_data:
            if len(transition_info) == 3:
                source_state, target_state, trigger_action = int(transition_info[0]), int(transition_info[1]), \
                                                             transition_info[2]
                transition = Transition(self.app_id)
                transition.set_source_id(self.state_list[source_state].state_id)
                transition.set_target_id(self.state_list[target_state].state_id)
                transition.set_transition_id(transition_id)
                event = Event(trigger_action, '', '')
                transition.set_event(event)
                self.transitions.append(transition)  # 转换为Transition类型，并存入transitions
            else:  # len(transition_info) == 4
                source_state, target_state, trigger_action, trigger_identifier = int(transition_info[0]), int(
                    transition_info[1]), transition_info[2], transition_info[3]
                transition = Transition(self.app_id)
                transition.set_source_id(self.state_list[source_state].state_id)
                transition.set_target_id(self.state_list[target_state].state_id)
                transition.set_transition_id(transition_id)
                event = Event(trigger_action, trigger_identifier, '')
                transition.set_event(event)
                self.transitions.append(transition)  # 转换为Transition类型，并存入transitions
            transition_id += 1

        scenarios_data = db.get_scenarios_by_app_id(app_id)

        for scenario in scenarios_data:
            scenario_name = scenario[0]
            desc = scenario[1]
            path = scenario[2]
            new_scenarios = Scenario(self.app_id)
            new_scenarios.set_name(scenario_name)
            new_scenarios.set_des(desc)
            new_scenarios.set_path(path)
            self.scenarios.append(new_scenarios)

    def Save_Model_To_Database(self):
        """
        将内存中的Model保存到数据库
        """
        print(self.app_id)
        db = DBAction()
        # app_id = db.get_app_id(self.package_name)

        db.change_db("Mergeresult")   #用于存储Model结果的数据库

        db.insert_row_app_info(self.app_id,self.apk_name,self.package_name,self.version)
        for state in self.state_list:
            db.insert_row_state(self.app_id, state.state_id, state.activity_name, state.picture, state.layout)
        for transition in self.transitions:
            # db.insert_row_transition(self.app_id, transition.source_state, transition.target_state, transition.event.trigger_action, transition.event.trigger_identifier, transition.event.condition)
            #SOURCE_STATE / TARGET_STATE UNKNOWN
            db.insert_row_transition(self.app_id, -1, -1,
                                     transition.event.trigger_action, transition.event.trigger_identifier,
                                     transition.event.conditions)
        for scenario in self.scenarios:
            db.insert_row_scenarios(self.app_id, scenario.scenario_name, scenario.description, scenario.path)
    
    def Save_Model_To_Local(self, out_dir):
        # 将内存中的Model保存到文件夹
        """
        保存模型到文件
        :param out_dir: 目标文件夹
        """
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        out_path = out_dir + 'screens/'  # out_path: res/screens
        if not os.path.exists(out_path):
            os.mkdir(out_path)
        for state in self.state_list:
            layout_file = os.path.join(out_path, str(state.state_id) + '.uix')  # layout_file: res/screens/0.uix
            with open(layout_file, 'w') as f:
                f.write(state.layout)
            f.close()
            state.init_pic(out_path)

        with open(out_dir + 'app_info.lst', 'w') as f:
            f.write(self.apk_name + '\n')
            f.write(self.package_name + '\n')
            f.write(self.apk_version + '\n')
        f.close()
        with open(out_dir + 'transitions.lst', 'w') as f:
            for transition in self.transitions:
                f.write(transition.get_line() + '\n')
        f.close()
        with open(out_dir + 'scenarios.lst', 'w') as f:
            for scenario in self.scenarios:
                f.write(str(scenario) + '\n')
        f.close()
        with open(out_dir + 'window_info.lst', 'w') as f:
            for state in self.state_list:
                f.write(str(state.state_id) + ' ' + state.get_activity_name() + '\n')
        f.close()

    def Print_Model(self):
        # 打印出Model的内容
        print("============== %s ===============" % self.package_name)
        print('-------- state_info --------')
        for state in self.state_list:
            print(state.state_id, state.activity_name)
        print('------ transitions_info ------')
        for transition in self.transitions:
            print(transition.source_id, transition.target_id, transition.event.trigger_action,
                  transition.event.trigger_identifier)
        print('------ scenarios_info ------')
        for scenario in self.scenarios:
            print(scenario.scenario_name, scenario.path)

    def generate_json(self):
        # 将内存中的跳转数据转换为一个用dict表示的跳转表
        data = {}
        for transition in self.transitions:
            source_id = transition.get_source_id()
            target_id = transition.get_target_id()
            if source_id < target_id:
                if source_id not in data:
                    data[source_id] = [target_id]
                elif target_id not in data[source_id]:
                    data[source_id].append(target_id)
        return data

    def generate_trans_df(self):  # 生成包含跳转及对应事件的dataframe
        self.trans_df = pd.DataFrame(columns=('source_id', 'target_id', 'action', 'identifier'))
        for transition in self.transitions:
            t_dict = {'source_id': transition.get_source_id(),
                      'target_id': transition.get_target_id(),
                      'action': transition.get_event().get_trigger_action(),
                      'identifier': transition.get_event().get_trigger_identifier()}
            self.trans_df = self.trans_df.append(t_dict, ignore_index=True)

    def generate_ifml_json(self):
        gap = 40
        elements = []
        data = []
        self.genarate_element(0, data, elements)

    def create_element(self, id, type, x, y, width, heigth):
        element = {"id": id,
                   "type": type,
                   "attributes": {
                       "name": id,
                       "default": False,
                       "landmark": False,
                       "xor": False
                   },
                   "metadata": {
                       "graphics": {
                           "position": {
                               "x": x,
                               "y": y
                           },
                           "size": {
                               "width": width,
                               "height": heigth
                           }
                       }
                   }
                   }
        return element

    def generate_element(self, root, data, elements):
        if root not in data:
            element = {"id": root,
                       "type": "ifml.ViewContainer",
                       "attributes": {
                           "name": root,
                           "default": False,
                           "landmark": False,
                           "xor": False
                       },
                       "metadata": {
                           "graphics": {
                               "position": {
                                   "x": 40,
                                   "y": 100
                               },
                               "size": {
                                   "width": 180,
                                   "height": 100
                               }
                           }
                       }
                       }
            return {"id": root}
        children = []

    def tree_to_dict(self, root, data):
        if root not in data:
            return {"id": root}
        children = []
        for state_id in data[root]:
            child = self.tree_to_dict(state_id, data)
            children.append(child)
        return {"id": root, "children": children}