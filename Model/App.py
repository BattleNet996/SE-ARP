'''

存储数据库中每个app信息的存储单元；
与数据库表项的对应：
appId->app_id
apkName->apk_name
packageName->package_name
version->version
states->相应app中所有的state数据，以<state_id,state_info>键值对存入hashMap中。
scenarios->相应app中的场景集合

author zhouxinyu

'''

from AppRunningPath import AppRunningPath


class App:

    def __init__(self, id=-1, apk=None, pck=None, v=None):
        self.app_id = id
        self.apk_name = apk
        self.package_name = pck
        self.apk_version = v

        self.states = {}
        self.app_running_path = AppRunningPath()
        self.scenarios = []

    def set_id(self, id):
        self.app_id = id

    def set_apk_name(self, apk):
        self.apk_name = apk

    def set_package_name(self, pck):
        self.package_name = pck

    def set_version(self, v):
        self.apk_version = v

    def set_states(self, s):
        if self.states == None:
            self.states = {}

    def set_app_running_path(self, arp):
        self.app_running_path = arp

    def set_scenarios(self, sc):
        if self.scenarios == None:
            self.scenarios = []
        self.scenarios.extend(sc)

    def get_id(self):
        return self.app_id

    def get_apk_name(self):
        return self.apk_name

    def get_package_name(self):
        return self.package_name

    def get_version(self):
        return self.apk_version

    def get_states(self):
        return self.states

    def get_app_running_path(self):
        return self.app_running_path

    def get_scenarios(self):
        return self.scenarios


    def __str__(self):
        st = ''
        for key in self.states:
            st += str(self.states[key])
            st += '\n'
        sc = ''
        for scene in self.scenarios:
            sc += str(scene)
            sc += '\n'
        return "[app_id:" + str(self.app_id) + " apk_name:" + str(self.apk_name) + " package_name:" + str(
            self.package_name) + " version:" + self.apk_version + " states:" + st + " appRunningPath:" + str(
            self.app_running_path) + " scenarios:" + sc + "]"