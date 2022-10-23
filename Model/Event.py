'''

将transition中的Event单独成类。
与数据库transition表的对应关系：
triggerAction->trigger_action
triggerIdentifier->trigger_identifier
conditions->conditions

@author zhouxinyu

'''


class Event:

    def __init__(self, ta, ti, con):
        self.trigger_action = ta
        self.trigger_identifier = ti
        self.conditions = con

    def get_trigger_action(self):
        return self.trigger_action

    def set_trigger_action(self, ta):
        self.trigger_action = ta

    def get_trigger_identifier(self):
        return self.trigger_identifier

    def set_trigger_identifier(self, ti):
        self.trigger_identifier = ti

    def get_conditions(self):
        return self.conditions

    def set_conditions(self, con):
        self.conditions = con