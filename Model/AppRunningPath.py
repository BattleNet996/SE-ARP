'''

相应app中的所有Transition以<transition_id,transition_info>键值对存入hashMap

author zhouxinyu

'''


class AppRunningPath:

    def __init__(self, ts={}):
        self.transitions = {}
        self.transitions.update(ts)

    def get_trans(self):
        return self.transitions

    def get_state_related_transition(self, state_id):
        result = {}
        for key in self.transitions:
            if self.transitions[key].get_source_id() == state_id:
                result[key] = self.transitions[key]
        return result

    def __str__(self):
        re = ''
        for key in self.transitions:
            re += str(self.transitions[key])
            re += '\n'
        return re