#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2021/6/2 13:56 下午
# @Author  : Tang Jiaxin，Chen wenjie，Wang Jiajie
# 对一个app的多个模型进行合并
# 1、合并state_list
# 2、合并transition
# 3、根据得到的state_list，确定当前app所包含的states

import sys
sys.path.append('../Model')
from BuildModel import Model
from Transition import Transition
from Event import Event
import pandas as pd
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from networkx.drawing.nx_pydot import to_pydot
import networkx as nx
import random


class Merge:
    def __init__(self):  # 初始构造函数
        self.app_id = None
        self.app_apk_name = None
        self.app_package_name = None
        self.app_version = None
        self.model_list = []  # 待合并的model列表
        self.res_state_list = []  # 合并后的state_list
        self.res_transitions = []  # 合并后的transitions
        self.res_states = {}  # 合并后的states
    
    def get_model_id(self):
        """读取模型列表中的模型以获取app_id"""
        try:
            return self.model_list[0].app_id
        except:
            return -1
    
    def add_model(self, model):  # 向model_list中添加一个模型
        if len(self.model_list) == 0:
            self.app_id = model.get_id()
            self.app_apk_name = model.get_apk_name()
            self.app_package_name = model.get_package_name()
            self.app_version = model.get_version()
        elif model.get_id() != self.app_id:
            return
        self.model_list.append(model)

    def get_res_model(self):  # 返回一个合并后的模型
        res_model = Model()
        res_model.set_id(self.get_model_id())
        print(res_model.app_id)
        res_model.set_apk_name(self.app_apk_name)
        res_model.set_package_name(self.app_package_name)
        res_model.set_version(self.app_version)
        res_model.state_list = self.res_state_list
        res_model.transitions = self.res_transitions
        res_model.states = self.res_states
        return res_model
    
    def search_state(self, state_list, state):  # 在state_list中查找某个state，返回其下标
        for i in range(len(state_list)):
            if self.cmp_xml(state_list[i].layout, state.layout) > 0.9:
                return i
        return -1

    def add_states(self, model):
        # 将当前model中的所有state加入res_state_list中，返回旧state_id与新state_id的对应关系字典
        res_dict = {}
        for state in model.state_list:
            # 在res_state_list中查找state是否已经存在
            new_id = self.search_state(self.res_state_list, state)
            if new_id != -1:  # 如果查找到，则更新state_id
                res_dict[state.get_state_id()] = new_id
                state.set_state_id(new_id)
            else:  # 如果没有查找到，则设置state_id，并将state加入res_state_list
                new_id = len(self.res_state_list)
                res_dict[state.get_state_id()] = new_id
                state.set_state_id(new_id)
                self.res_state_list.append(state)
        return res_dict

    def merge_models(self):
        # 建立一个用于存储合并后的transition信息的dataframe
        res_df = pd.DataFrame(columns=('source_id', 'target_id', 'action', 'identifier'))
        for model in self.model_list:  # 依次遍历每个model
            model.generate_trans_df()  # 为model建立trans_df，用于合并
            t_dict = self.add_states(model)  # 将model的state加入到res_state_list中
            # 根据获得的对应结果，更新transitions中的state_id
            for transition in model.transitions:
                transition.set_source_id(t_dict[transition.get_source_id()])
                transition.set_target_id(t_dict[transition.get_target_id()])
            # 根据获得的对应结果，更新trans_df中的state_id，并将更新后的row加入res_df
            for index, row in model.trans_df.iterrows():
                row['source_id'] = t_dict[row['source_id']]
                row['target_id'] = t_dict[row['target_id']]
                res_df = res_df.append(row, ignore_index=True)
        res_df = res_df.drop_duplicates()  # 对合并完成后的dataframe进行去重
        self.res_transitions = []
        transition_id = 0
        # 根据去重后的dataframe生成合并后的transitions
        for index, row in res_df.iterrows():
            transition = Transition()
            transition.set_transition_id(transition_id)
            transition.set_source_id(row['source_id'])
            transition.set_target_id(row['target_id'])
            event = Event(row['action'], row['identifier'], '')
            transition.set_event(event)
            transition_id += 1
            self.res_transitions.append(transition)
        # 根据res_state_list生成states
        for state in self.res_state_list:
            self.res_states[state.state_id] = state

    def cmp_xml(self, layout1, layout2):  # 计算两个xml字符串的相似度
        # tree1 = ET.parse(file1)
        # tree2 = ET.parse(file2)  # 根据xml文件建立element tree
        # root1 = tree1.getroot()
        # root2 = tree2.getroot()  # 获取两棵树的根节点
        root1 = ET.fromstring(layout1)
        root2 = ET.fromstring(layout2)
        return self.cmp_xml_node(root1, root2)

    def cmp_xml_node(self, node1, node2):  # 计算以两个节点为根的子树的相似度
        if node1.tag != node2.tag:  # 若两个节点的名称不同
            return 0  # 两个节点的相似度为0
        if len(node1) == 0 and len(node2) == 0:  # 若两个节点均为叶子节点
            return self.cmp_xml_leaf(node1, node2)
        if len(node1) == 0 or len(node2) == 0:  # 若node1或node2是叶子节点而另一个不是
            return 0
        child_dict1 = self.genenate_child_dict(node1)  # 生成node1对应的子节点字典
        child_dict2 = self.genenate_child_dict(node2)  # 生成node2对应的子节点字典
        sim_value = 0  # 两节点的相似度评分
        for tag1, child_list1 in child_dict1.items():  # 依次遍历node1的子节点字典
            child_list2 = child_dict2.get(tag1)  # 在node2的子节点字典中查找由同名子节点构成的列表
            if child_list2 is None:  # 若查找不到
                continue
            sim_value += self.cmp_xml_same_tag(child_list1, child_list2)  # 计算两个同名的子节点列表的相似度
        return sim_value / max(len(child_dict1), len(child_dict2))

    def cmp_xml_same_tag(self, list1, list2):  # 计算两个同名子节点列表的相似度
        sim_value = 0  # 两列表的相似度评分
        sim_values = np.zeros((len(list1), len(list2)))  # 创建评分矩阵
        for i in range(len(list1)):
            for j in range(len(list2)):
                sim_values[i, j] = self.cmp_xml_node(list1[i], list2[j])  # 计算两两之间的相似度
        while sim_values.shape[0] != 0 and sim_values.shape[1] != 0:
            max_index = np.argmax(sim_values)  # 从所有相似度中找最大值所在的位置
            max_row = max_index // sim_values.shape[1]
            max_col = max_index % sim_values.shape[1]  # 计算最大值所在的行和列
            max_sim_value = sim_values[max_row, max_col]
            if max_sim_value == 0:
                break
            sim_value += max_sim_value
            sim_values = np.delete(sim_values, max_row, axis=0)
            sim_values = np.delete(sim_values, max_col, axis=1)  # 删除最大值所在的行和列
        return sim_value / max(len(list1), len(list2))
    
    def genenate_child_dict(self, node):  # 产生某个节点的子节点字典
        children = {}
        for child in node:
            if child.tag not in children:
                children[child.tag] = [child]
            else:
                children[child.tag].append(child)
        return children

    def cmp_xml_node_key(self, key, value1, value2):  # 根据属性名称，计算两个属性值的相似度
        if key == 'index':
            return 1
        return value1 == value2

    def cmp_xml_leaf(self, node1, node2):  # 计算两个同名叶子节点的相似度
        attrib1 = node1.attrib
        attrib2 = node2.attrib
        sim_value = 0
        for key1, value1 in attrib1.items():  # 依次遍历node1的属性列表
            value2 = attrib2.get(key1)  # 在node2中查找相应属性的属性值
            if value2 is None:  # 如果node2中不存在该名字的属性
                continue
            sim_value += self.cmp_xml_node_key(key1, value1, value2)  # 计算两个属性值的相似度
        return sim_value / max(len(attrib1), len(attrib2))
    
    def hierarchy_pos(self, G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
        '''
        G: the graph (must be a tree)

        root: the root node of current branch
        - if the tree is directed and this is not given,
          the root will be found and used
        - if the tree is directed and this is given, then
          the positions will be just for the descendants of this node.
        - if the tree is undirected and not given,
          then a random choice will be used.

        width: horizontal space allocated for this branch - avoids overlap with other branches

        vert_gap: gap between levels of hierarchy

        vert_loc: vertical location of root

        xcenter: horizontal location of root
        '''
        if not nx.is_tree(G):
            raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

        if root is None:
            if isinstance(G, nx.DiGraph):
                root = next(iter(nx.topological_sort(G)))  # allows back compatibility with nx version 1.11
            else:
                root = random.choice(list(G.nodes))

        def _hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
            '''
            see hierarchy_pos docstring for most arguments

            pos: a dict saying where all nodes go if they have been assigned
            parent: parent of this branch. - only affects it if non-directed

            '''

            if pos is None:
                pos = {root: (xcenter, vert_loc)}
            else:
                pos[root] = (xcenter, vert_loc)
            children = list(G.neighbors(root))
            if not isinstance(G, nx.DiGraph) and parent is not None:
                children.remove(parent)
            if len(children) != 0:
                dx = width / len(children)
                nextx = xcenter - width / 2 - dx / 2
                for child in children:
                    nextx += dx
                    pos = _hierarchy_pos(G, child, width=dx, vert_gap=vert_gap,
                                         vert_loc=vert_loc - vert_gap, xcenter=nextx,
                                         pos=pos, parent=root)
            return pos

        return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

    def model1_transitions_visualization(self, model):  # type1对应的model1可视化
        source_id_list = []
        target_id_list = []
        test_list = [0]
        data_list = []
        j = 0
        for transition in model.transitions:
            source_id_list.append(transition.source_id)
            target_id_list.append(transition.target_id)
        visualization_tuple = sorted(zip(source_id_list, target_id_list))
        #print(visualization_tuple)  # visualization_tuple索引0存储souece_id,索引1存储target_id
        plt.figure(figsize=(48, 36))
        for i in range(len(visualization_tuple)):  # 依次遍历visualization_tuple的元组
            if visualization_tuple[i][0] == test_list[j]:  # 如果visualization_tuple中的source_id已存在于test_list
                data_list.append(visualization_tuple[i])  # 将元组添加至data_list
            else:  #使用现有data_list中的元组画图
                G = nx.Graph()
                G.add_edges_from(data_list)
                k = test_list[j]  #确定source_id作为根节点
                try:
                    plt.subplot(9, 9, 0 + len(test_list))  #创建子图
                    nx.draw(G, with_labels=True, node_size=300)
                    G.remove_node(k)
                except:
                    pass
                j += 1
                test_list.append(visualization_tuple[i][0])
                data_list.clear()  #画图后清空data_list
                data_list.append(visualization_tuple[i])  #添加新元组
                plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
        plt.savefig('model1.png')

    def model2_transitions_visualization(self, model):  # type1对应的model2可视化
        source_id_list = []
        target_id_list = []
        test_list = [0]
        data_list = []
        j = 0
        for transition in model.transitions:
            source_id_list.append(transition.source_id)
            target_id_list.append(transition.target_id)
        visualization_tuple = sorted(zip(source_id_list, target_id_list))
        #print(visualization_tuple)
        plt.figure(figsize=(16, 12))
        for i in range(len(visualization_tuple)):
            if visualization_tuple[i][0] == test_list[j]:
                data_list.append(visualization_tuple[i])
            else:
                G = nx.Graph()
                G.add_edges_from(data_list)
                k = test_list[j]
                try:
                    plt.subplot(330 + len(test_list))
                    nx.draw(G, with_labels=True, node_size=300)
                    G.remove_node(k)
                except:
                    pass
                j += 1
                test_list.append(visualization_tuple[i][0])
                data_list.clear()
                data_list.append(visualization_tuple[i])
                plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
        plt.savefig('model2.png')
    
    def model1_transitions_visualization2(self, model):  # type2对应的model1可视化
        source_id_list = []
        target_id_list = []
        test_list = [0]
        data_list = []
        dot_list = []
        j = 0
        for transition in model.transitions:
            source_id_list.append(transition.source_id)
            target_id_list.append(transition.target_id)
        visualization_tuple = sorted(zip(source_id_list, target_id_list))
        #print(visualization_tuple)
        plt.figure(figsize=(48, 36))
        for i in range(len(visualization_tuple)):
            if visualization_tuple[i][0] == test_list[j]:
                data_list.append(visualization_tuple[i])
            else:
                G = nx.Graph()
                k = test_list[j]
                plt.subplot(9, 9, 0 + len(test_list))
                plt.axis('off')
                try:
                    G.add_edges_from(data_list)
                    pos = self.hierarchy_pos(G, k)
                    nx.draw(G, pos=pos, with_labels=True, node_size=300)
                except:  #source_id与target_id相同时使用dot画图
                    G.add_edges_from(data_list)
                    dot_list.append(j + 1)
                    P = to_pydot(G)
                    P.write_jpeg('pydot.png')
                    plt.imshow(Image.open('pydot.png'))
                G.remove_node(k)
                j += 1
                test_list.append(visualization_tuple[i][0])
                data_list.clear()
                data_list.append(visualization_tuple[i])
                plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
        plt.savefig('model1_2.png')

    def model2_transitions_visualization2(self, model):  # type2对应的model2可视化
        source_id_list = []
        target_id_list = []
        test_list = [0]
        data_list = []
        dot_list = []
        j = 0
        for transition in model.transitions:
            source_id_list.append(transition.source_id)
            target_id_list.append(transition.target_id)
        visualization_tuple = sorted(zip(source_id_list, target_id_list))
        #print(visualization_tuple)
        plt.figure(figsize=(16, 12))
        for i in range(len(visualization_tuple)):
            if visualization_tuple[i][0] == test_list[j]:
                data_list.append(visualization_tuple[i])
            else:
                G = nx.Graph()
                plt.subplot(330 + len(test_list))
                plt.axis('off')
                k = test_list[j]
                try:
                    G.add_edges_from(data_list)
                    pos = self.hierarchy_pos(G, k)
                    nx.draw(G, pos=pos, with_labels=True, node_size=300)
                except:
                    G.add_edges_from(data_list)
                    dot_list.append(j + 1)
                    P = to_pydot(G)
                    P.write_jpeg('pydot.png')
                    plt.imshow(Image.open('pydot.png'))
                G.remove_node(k)
                j += 1
                test_list.append(visualization_tuple[i][0])
                data_list.clear()
                data_list.append(visualization_tuple[i])
                plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
        plt.savefig('model2_2.png')
    
    def model1_transitions_visualization3(self, model):  # type3对应的model1可视化
        source_id_list = []
        target_id_list = []
        test_list = [0]
        data_list = []
        j = 0
        for transition in model.transitions:
            source_id_list.append(transition.source_id)
            target_id_list.append(transition.target_id)
        visualization_tuple = sorted(zip(source_id_list, target_id_list))
        #print(visualization_tuple)
        plt.figure(figsize=(48, 36))
        for i in range(len(visualization_tuple)):
            if visualization_tuple[i][0] == test_list[j]:
                data_list.append(visualization_tuple[i])
            else:
                G = nx.Graph()
                k = test_list[j]
                plt.subplot(9, 9, 0 + len(test_list))
                plt.axis('off')
                G.add_edges_from(data_list)
                P = to_pydot(G)
                P.write_jpeg('pydot.png')
                plt.imshow(Image.open('pydot.png'))
                G.remove_node(k)
                j += 1
                test_list.append(visualization_tuple[i][0])
                data_list.clear()
                data_list.append(visualization_tuple[i])
                plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
        plt.savefig('model1_3.png')

    def model2_transitions_visualization3(self, model):  # type3对应的model2可视化
        source_id_list = []
        target_id_list = []
        test_list = [0]
        data_list = []
        j = 0
        for transition in model.transitions:
            source_id_list.append(transition.source_id)
            target_id_list.append(transition.target_id)
        visualization_tuple = sorted(zip(source_id_list, target_id_list))
        plt.figure(figsize=(16, 12))
        for i in range(len(visualization_tuple)):
            if visualization_tuple[i][0] == test_list[j]:
                data_list.append(visualization_tuple[i])
            else:
                G = nx.Graph()
                plt.subplot(330 + len(test_list))
                plt.axis('off')
                k = test_list[j]
                G.add_edges_from(data_list)
                P = to_pydot(G)
                P.write_jpeg('pydot.png')
                plt.imshow(Image.open('pydot.png'))
                G.remove_node(k)
                j += 1
                test_list.append(visualization_tuple[i][0])
                data_list.clear()
                data_list.append(visualization_tuple[i])
                plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
        plt.savefig('model2_3.png')
    
    def res_transitions_visualization(self, model):  # type1对应的res可视化
        source_id_list = []
        target_id_list = []
        test_list = [0]
        data_list = []
        j = 0
        for transition in model.transitions:
            source_id_list.append(transition.source_id)
            target_id_list.append(transition.target_id)
        visualization_tuple = sorted(zip(source_id_list, target_id_list))
        #print(visualization_tuple)
        plt.figure(figsize=(48, 36))
        for i in range(len(visualization_tuple)):
            if visualization_tuple[i][0] == test_list[j]:
                data_list.append(visualization_tuple[i])
            else:
                G = nx.Graph()
                G.add_edges_from(data_list)
                k = test_list[j]
                plt.subplot(9, 7, 0 + len(test_list))
                nx.draw(G, with_labels=True, node_size=300)
                G.remove_node(k)
                j += 1
                test_list.append(visualization_tuple[i][0])
                data_list.clear()
                data_list.append(visualization_tuple[i])
                plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
        plt.savefig('merge.png')

    def res_transitions_visualization2(self, model):  # type2对应的res可视化
        source_id_list = []
        target_id_list = []
        test_list = [0]
        data_list = []
        dot_list = []
        j = 0
        for transition in model.transitions:
            source_id_list.append(transition.source_id)
            target_id_list.append(transition.target_id)
        visualization_tuple = sorted(zip(source_id_list, target_id_list))
        #print(visualization_tuple)
        plt.figure(figsize=(48, 36))
        for i in range(len(visualization_tuple)):
            if visualization_tuple[i][0] == test_list[j]:
                data_list.append(visualization_tuple[i])
            else:
                G = nx.Graph()
                plt.subplot(9, 7, 0 + len(test_list))
                plt.axis('off')
                k = test_list[j]
                try:
                    G.add_edges_from(data_list)
                    pos = self.hierarchy_pos(G, k)
                    nx.draw(G, pos=pos, with_labels=True, node_size=300)
                except:
                    G.add_edges_from(data_list)
                    dot_list.append(j + 1)
                    P = to_pydot(G)
                    P.write_jpeg('pydot.png')
                    plt.imshow(Image.open('pydot.png'))
                G.remove_node(k)
                j += 1
                test_list.append(visualization_tuple[i][0])
                data_list.clear()
                data_list.append(visualization_tuple[i])
                plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
        plt.savefig('merge_2.png')

    def res_transitions_visualization3(self, model):  # type3对应的res可视化
        source_id_list = []
        target_id_list = []
        test_list = [0]
        data_list = []
        j = 0
        for transition in model.transitions:
            source_id_list.append(transition.source_id)
            target_id_list.append(transition.target_id)
        visualization_tuple = sorted(zip(source_id_list, target_id_list))
        #print(visualization_tuple)
        plt.figure(figsize=(48, 36))
        for i in range(len(visualization_tuple)):
            if visualization_tuple[i][0] == test_list[j]:
                data_list.append(visualization_tuple[i])
            else:
                G = nx.Graph()
                plt.subplot(9, 7, 0 + len(test_list))
                plt.axis('off')
                k = test_list[j]
                G.add_edges_from(data_list)
                P = to_pydot(G)
                P.write_jpeg('pydot.png')
                plt.imshow(Image.open('pydot.png'))
                G.remove_node(k)
                j += 1
                test_list.append(visualization_tuple[i][0])
                data_list.clear()
                data_list.append(visualization_tuple[i])
                plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
        plt.savefig('merge_3.png')

    def get_model_graph(self, type):
        plt.figure(figsize=(48, 36))
        if type == 1:
            plt.subplot(2, 2, 1)
            plt.title('model1')
            plt.imshow(Image.open('model1.png'))
            plt.axis('off')
            plt.subplot(2, 2, 2)
            plt.title('model2')
            plt.imshow(Image.open('model2.png'))
            plt.axis('off')
            plt.subplot(2, 2, 3)
            plt.title('merge')
            plt.imshow(Image.open('merge.png'))
            plt.axis('off')
        elif type == 2:
            plt.subplot(2, 2, 1)
            plt.title('model1')
            plt.imshow(Image.open('model1_2.png'))
            plt.axis('off')
            plt.subplot(2, 2, 2)
            plt.title('model2')
            plt.imshow(Image.open('model2_2.png'))
            plt.axis('off')
            plt.subplot(2, 2, 3)
            plt.title('merge')
            plt.imshow(Image.open('merge_2.png'))
            plt.axis('off')
        elif type == 1:
            plt.subplot(2, 2, 1)
            plt.title('model1')
            plt.imshow(Image.open('model1_3.png'))
            plt.axis('off')
            plt.subplot(2, 2, 2)
            plt.title('model2')
            plt.imshow(Image.open('model2_3.png'))
            plt.axis('off')
            plt.subplot(2, 2, 3)
            plt.title('merge')
            plt.imshow(Image.open('merge_3.png'))
            plt.axis('off')
        plt.savefig('total.png')
        plt.show()