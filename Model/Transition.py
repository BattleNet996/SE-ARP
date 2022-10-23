#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/5/12 0:50 下午
# @Author  : Chen Wenjie

# 1. 新增get_line()类方法，用于bulid_model.py中save_model()函数调用。
# 2. 修改__str__ ，与transition类最新数据成员适配。

'''

迁移类，与数据库transition表的对应关系：
appId->app_id
transitionId->transition_id
sourceId->source_id
targetId->target_id
triggerAction->trigger_action
triggerIdentifier->trigger_identifier
condition->conditions

author zhouxinyu

'''

from Model.Event import Event


class Transition:

    def __init__(self, id=-1):
        self.transition_id = -1
        self.app_id = id
        self.source_id = -1
        self.target_id = -1
        self.event = None

    def set_transition_id(self, id):
        self.transition_id = id

    def set_source_id(self, id):
        self.source_id = id

    def set_target_id(self, id):
        self.target_id = id

    def set_event(self, eve):
        self.event = eve

    def get_transition_id(self):
        return self.transition_id

    def get_source_id(self):
        return self.source_id

    def get_target_id(self):
        return self.target_id

    def get_event(self):
        return self.event

    def get_line(self):

        if self.event.trigger_identifier != "":
            return str(self.get_source_id()) + ' ' + str(self.get_target_id()) + ' ' + self.event.trigger_action + ' ' + self.event.trigger_identifier
        else:
            return str(self.get_source_id()) + ' ' + str(self.get_target_id()) + ' ' + self.event.trigger_action

    def __str__(self):
        return "[transition_id:" + str(self.transition_id) + " app_id:" + str(self.app_id) + " source->target:" + str(
            self.source_id) + "->" + str(self.target_id) + " trigger_action:" + str(
            self.event.get_trigger_action()) + " trigger_identifier:" + str(
            self.event.get_trigger_identifier()) + " conditions:" + str(self.event.get_conditions()) + "]"