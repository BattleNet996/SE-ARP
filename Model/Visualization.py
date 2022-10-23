# -*- encoding:utf-8 -*-
#!/usr/bin/env python
# @Time    : 2021/7/11 0:50 上午
# @Author  : Chen Wenjie

# 1. 以页面为节点，页面之间的联系方式为边，定义图类
# 2. 基于界面关系图进行可视化，并生成circle与force两种不同类型的关系图

from collections import defaultdict
import json
import os
from pyecharts import options as opts
from pyecharts.charts import Graph, Page
import pyecharts.charts
import numpy as np
import pandas as pd
import random

# --------------- nested Vertex class ------------------

class Vertex:
    """创建节点类"""

    def __init__(self, x, times):
        """初始化节点,x为节点的value, times为节点出现的频次"""
        vertex = {}
        self.element = x
        self.times = times
        try:
            vertex["name"] = x
            if times < 5:
                vertex["symbolSize"] = 15
                vertex["category"] = 2
                color = "#FF0000"
            elif times <= 15:
                vertex["symbolSize"] = 35
                vertex["category"] = 1
                color = "#3CB371"
            else:
                vertex["symbolSize"] = 50
                vertex["category"] = 0
                color = "#9400D3"
        except:
            vertex["symbolSize"] = 10
            vertex["category"] = 3
            color = "#00BFFF"
        try:
            vertex["value"] = "连接页面数：" + str(times)

        except:
            vertex["value"] = "连接页面数：0"
        vertex['draggable'] = "True"
        # vertex["itemStyle"] = {"normal":{"color":color}}
        self.vertex = vertex

    def element(self):
        """返回节点的元素值"""
        return self.element

    def vertex(self):
        """返回节点"""
        return self.vertex

    def __hash__(self):
        """允许节点作为映射的键"""
        return hash(id(self))


class Edge:
    """创建边类"""

    def __init__(self, u, v, x):
        """初始化边"""
        self.origin = u
        self.destination = v
        self.element = x

    def endpoints(self):
        """以元组的方式返回边的两个端点(u,v)"""
        return (self.origin, self.destination)

    def opposite(self, v):
        """假设顶点v是边的一个端点，返回另一个端点"""
        return self.destination if v is self.origin else self.origin

    def element(self):
        return self.element

    def __hash__(self):
        """实现边的映射"""
        return hash(self.origin, self.destination)


class Graph:
    """图类"""

    def __init__(self, vertex_count=0, directed=False):
        """首先创建个空图，默认为undirected"""
        self.vertices = []  # 这里存储了图的节点
        self.vertex_count = vertex_count  # 这里存储了图的节点数
        self.adjacency_matrix = defaultdict(list)  # 这里存储了图的边（字典）
        self.edges = []  # 这里存储了图的边（列表，节点的连接关系）
        self.links = []  # 这里存储了图的边（列表，用于绘制关系图）

    def read_edge(self, res):
        """从res模型中读取所有的页面连接信息"""
        # 三元组的形式从模型中读取节点跳转信息
        edges = []
        for i in range(len(res.transitions)):
            edges.append(
                tuple((res.transitions[i].get_source_id(),
                       res.transitions[i].get_target_id(),
                       res.transitions[i].get_event().get_trigger_action())
                      ))

        # 将读取的边附给图类的edges
        self.edges = edges

    def insert_edge(self):
        """用加边的方式添加图的节点"""
        for i in range(len(self.edges)):
            u = self.edges[i][0]
            v = self.edges[i][1]
            self.adjacency_matrix[u].append(v)

    def insert_vertex(self):
        """插入节点"""
        # 获取最后一个页面的编号
        max = 0
        for i in range(len(self.edges)):
            if self.edges[i][0] > max:
                max = self.edges[i][0]
            if self.edges[i][1] > max:
                max = self.edges[i][1]

        # 测算每个节点所连通的节点数
        aDict = {}
        for i in range(len(self.edges)):
            aDict[self.edges[i][0]] = aDict.get(self.edges[i][0], 0) + 1

        print("max:"+str(max))
        # 生成系列节点
        for i in range(1, max + 1):
            try:
                v = Vertex(i, aDict[i])
            except:
                v = Vertex(i, 0)
            self.vertices.append(v.vertex)
            self.vertex_count += 1

    def add_links(self):
        """插入节点连接，用于生成关系图"""
        for i in range(len(self.edges)):
            self.links.append(
                {
                    "source": self.edges[i][0],
                    "target": self.edges[i][1],
                    "value": self.edges[i][2]
                }
            )


    def generate_graph(self, res):
        """总调函数，传入合并后的模型，生成图"""
        self.read_edge(res)
        self.insert_vertex()
        self.insert_edge()
        self.add_links()

    def visualization(self):
        """关系图的可视化"""
        categories = [
            {
                "name": "重要节点"
            },
            {
                "name": "次重要节点"
            },
            {
                "name": "一般节点"
            },
            {
                "name": "孤立节点"
            }
        ]

        # circular layout
        graph = (
            pyecharts.charts.Graph(init_opts=opts.InitOpts(width="1000px", height="800px"))
            .add("",
                 self.vertices,
                 self.links,
                 categories=categories,
                 repulsion=50,

                 linestyle_opts=opts.LineStyleOpts(curve=0.2),
                 is_rotate_label=True,
                 layout="circular",
                 label_opts=opts.LabelOpts(position="right"),
                 edge_label=opts.LabelOpts(
                     is_show=False, position="middle", formatter="{b} 的数据 {c}"
                 )
             )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="ARP路径关系图"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_left="2%", pos_top="20%"
                                        )
            )
        )
        graph.render("circle_layout_graph.html")

        # force layout
        graph = (
            pyecharts.charts.Graph(init_opts=opts.InitOpts(width="960px", height="800px"))
                .add("",
                     self.vertices,
                     self.links,
                     categories=categories,
                     repulsion=50,
                     edge_length=100,
                     gravity=0.05,
                     # linestyle_opts=opts.LineStyleOpts(curve=0.2),
                     is_rotate_label=True,
                     layout="force",
                     label_opts=opts.LabelOpts(position="right"),
                     edge_label=opts.LabelOpts(
                         is_show=False, position="middle", formatter="{b} 的数据 {c}"
                     )
                )
                .set_global_opts(
                title_opts=opts.TitleOpts(title="ARP路径关系图"),
                legend_opts=opts.LegendOpts(orient="vertical", pos_left="2%", pos_top="20%"
                                            )
            )
        )
        graph.render("force_layout_graph.html")

