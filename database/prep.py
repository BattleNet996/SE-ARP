#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/4 6:56 下午
# @Author  : Wang Guoxin

import os
from database.api import DBAction
import base64
import xml.etree.ElementTree

def convertToBinaryData(filepath):
    """
    将图片转化为二进制格式
    :param filepath: 图片地址
    :return: 二进制数据
    """
    with open(filepath, 'rb') as file:
        binary_data = file.read()
        encodestring = base64.b64encode(binary_data)
    return encodestring

def encode_layout(filepath):
    tree = xml.etree.ElementTree.parse(filepath)
    root = tree.getroot()
    return xml.etree.ElementTree.tostring(root).decode()

def read_q_testing_result(project_dir):
    """
    读取Q-testing探索App生成的结果
    :param project_dir: 项目文件夹地址
    :return: apk_name, package_name, version, states, jump_pairs
    """
    file = open(os.path.join(project_dir, 'app_info.lst'), 'r')
    apk_name = file.readline().strip()
    package_name = file.readline().strip()
    version = file.readline().strip()

    states = []
    file = open(os.path.join(project_dir, 'window_info.lst'), 'r')
    for l in file.readlines():
        line = l.split()
        state_id, activity_name = line[0], line[1]
        screen_shot_path = os.path.join(project_dir, 'temp-screen-shot', state_id+'.png')
        layout_file_path = os.path.join(project_dir, 'temp-gui-hierarchy', state_id+'.xml')
        if not os.path.exists(screen_shot_path):
            print(screen_shot_path + ' not exists')
            exit(0)
        if not os.path.exists(layout_file_path):
            print(layout_file_path + ' not exists')
            exit(0)
        binary_data = convertToBinaryData(screen_shot_path)
        layout = encode_layout(layout_file_path)
        states.append((line[0], line[1], binary_data, layout))

    jump_pairs = []
    file = open(os.path.join(project_dir, 'jump_pairs.lst'), 'r')
    for l in file.readlines():
        line = l.split(maxsplit=2)
        if len(line) == 3:
            action_str = line[2].strip()
            at_pos = action_str.find("@")
            # TODO 是否要记录不发生跳转的事件
            if line[0] != line[1]:
                if at_pos == -1:
                    jump_pairs.append([line[0], line[1], action_str])
                else:
                    action_str = action_str[at_pos + 1:]
                    if action_str.startswith('click') or action_str.startswith('clickLong') or action_str.startswith('edit'):
                        spilt_index = action_str.find('(')
                        action_type = action_str[:spilt_index]
                        action_identifier = action_str[spilt_index+1:-1]
                        #print([line[0], line[1], action_type, action_identifier])
                        jump_pairs.append([line[0], line[1], action_type, action_identifier])
                    else:
                        jump_pairs.append([line[0], line[1], action_str])
                        #print([line[0], line[1], action_str])
        else:
            print("WARNING: Skipped invalid record in " + os.path.join(project_dir, 'jump_pairs.lst'))
            print(line)

    return apk_name, package_name, version, states, jump_pairs

def read_scenario_info(project_dir):
    """
    读取功能场景及其路径
    :param project_dir: 项目文件夹地址
    :return: scenario_name, path
    """
    scenario_name_list = []
    path_list = []
    scenarios = os.listdir(os.path.join(project_dir, 'feature'))
    for scenario in scenarios:
        if scenario == '.DS_Store':
            continue
        scenario_name = scenario.split(' ')[0]
        path_str = scenario.split(' ')[1]
        scenario_name_list.append(scenario_name)
        path_list.append(path_str)

    return scenario_name_list, path_list

def process_project(project_path):
    """
    处理单个项目文件夹
    :param project_path: 项目文件夹路径
    :return:
    """
    apk_name, package_name, version, states, jump_pairs = read_q_testing_result(project_path)

    db = DBAction()
    package_name_list = db.get_all_app_package_name()
    if package_name in package_name_list:
        print("Skipped exist apk " + package_name)
        return

    # 插入 app_info
    db.insert_row_app_info(apk_name, package_name, version)
    app_id = db.get_app_id(package_name)

    if app_id != -1:
        # 插入 state
        for (state_id, activity_name, binary_data, layout) in states:
            db.insert_row_state(app_id, state_id, activity_name, binary_data, layout)

        # 插入 transition
        for jump_pair in jump_pairs:
            if len(jump_pair) == 3:
                source_state, target_state, trigger_action= jump_pair[0], jump_pair[1], jump_pair[2]
                db.insert_row_transition(app_id, source_state, target_state, trigger_action, '', '')
            elif len(jump_pair) == 4:
                source_state, target_state, trigger_action, trigger_identifier = jump_pair[0], jump_pair[1], jump_pair[2], jump_pair[3]
                db.insert_row_transition(app_id, source_state, target_state, trigger_action, trigger_identifier, '')
            else:
                print("WARNING: error jump_pair")

        # 插入功能场景及其路径
        # scenario_name_list, path_list = read_scenario_info(project_path)
        # for index in range(len(scenario_name_list)):
        #     print(app_id, scenario_name_list[index], '', path_list[index])
        #     db.insert_row_scenarios(app_id, scenario_name_list[index], '', path_list[index])


    print('## Project processed: ' + project_path)

def process_whole(path):
    """
    处理包含项目文件夹的整体文件夹
    :param path: 项目文件夹所在文件夹路径
    :return:
    """
    for f in os.listdir(path):
        project_path = os.path.join(path, f)
        if os.path.isdir(project_path):
            process_project(project_path)

if __name__ == "__main__":
    process_whole('/Users/wangguoxin/Projects/AppRepository/ProjectCollections/Q-testing-out/success')
    #process_project('/Users/wangguoxin/Projects/AppRepository/ProjectCollections/Q-testing-out/debug_output1/org.asdtm.goodweather_13')