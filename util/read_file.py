#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/7 4:08 下午
# @Author  : Wang Guoxin

"""
    从作业里读取模型信息，且作业中的各种文件应该是格式化过的，清理过的数据
"""

import os
import chardet
import xml.etree.ElementTree
import base64
import re


def get_file_encoding(path):
    f = open(path, 'rb')
    data = f.read()
    return chardet.detect(data).get('encoding')


def image2base64(filepath):
    """
    将图片转化为二进制格式
    :param filepath: 图片地址
    :return: 二进制数据的base64编码
    """
    with open(filepath, 'rb') as file:
        binary_data = file.read()
        encodestring = base64.b64encode(binary_data)
    return encodestring


def encode_layout(filepath):
    tree = xml.etree.ElementTree.parse(filepath)
    root = tree.getroot()
    return xml.etree.ElementTree.tostring(root).decode()


def read_app_info(project_path):
    author_id = None
    with open(os.path.join(project_path, 'app_info.lst'), 'r', encoding='utf-8') as f:
        lines = f.readlines()
        app_name = lines[0].strip()
        package_name = lines[1].strip()
        version = lines[2].strip()
    return app_name, package_name, version, author_id


def read_state_info(project_path):
    states = []
    state_activity_file = os.path.join(project_path, 'window_info.lst')
    file = open(state_activity_file, 'r', encoding=get_file_encoding(state_activity_file))

    for l in file.readlines():
        l = l.strip()
        line = l.split()
        state_id, activity_name = line[0], line[1]
        screen_shot_path = os.path.join(project_path, 'screens', state_id + '.png')
        layout_file_path = os.path.join(project_path, 'screens', state_id + '.uix')
        if not os.path.exists(screen_shot_path):
            print(screen_shot_path + ' not exists')
            exit(0)
        # 对于动态界面可能无法获取布局文件的情况，设layout为空字符
        if not os.path.exists(layout_file_path):
            print(layout_file_path + ' not exists')
            layout = ''
        else:
            layout = encode_layout(layout_file_path)
        binary_data = image2base64(screen_shot_path)
        states.append((state_id, activity_name, binary_data, layout))
    return states


def read_transitions(project_path):
    transitions = []
    file = open(os.path.join(project_path, 'jump_pairs.lst'), 'r')
    for line in file.readlines():
        line = line.strip()
        fields = re.split(r" (?![^(]*\))", line, maxsplit=3)
        if len(fields) == 3:
            transitions.append([fields[0], fields[1], fields[2]])
        elif len(fields) == 4:
            transitions.append([fields[0], fields[1], fields[2], fields[3]])
        else:
            print("WARNING: Skipped invalid record:" + line)
            print(len(fields))
    return transitions


def read_scenarios_info(project_path):
    scenarios_file = os.path.join(project_path, 'scenarios.lst')
    file = open(scenarios_file, 'r', encoding=get_file_encoding(scenarios_file))
    scenarios = []

    for line in file.readlines():
        if line.startswith('[功能名称]'):
            continue
        line = line.strip()
        fields = re.findall(r'[[](.*?)[]]', line)
        print(fields)
        scenarios.append([fields[0], fields[1], fields[2]])

    return scenarios