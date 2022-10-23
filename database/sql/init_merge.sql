CREATE DATABASE IF NOT EXISTS MergeResult;


CREATE TABLE IF NOT EXISTS MergeResult.app_info(
    app_id INT NOT NULL  PRIMARY KEY,
    apk_name VARCHAR(128) NOT NULL,
    package_name VARCHAR(128) NOT NULL,
    version VARCHAR(32) ,
    author VARCHAR(32)
);

CREATE TABLE IF NOT EXISTS MergeResult.state(
    state_id INT  NOT NULL PRIMARY KEY,
    app_id INT  NOT NULL,
    activity_name VARCHAR(128) ,
    screen_shot mediumblob ,
    layout LONGTEXT ,
    FOREIGN KEY (app_id) REFERENCES app_info(uid)
);

CREATE TABLE IF NOT EXISTS MergeResult.transition(
    transition_id BigInt  NOT NULL AUTO_INCREMENT PRIMARY KEY,
    app_id INT  NOT NULL,
    source_state INT  ,
    target_state INT  ,
    trigger_action TEXT ,
    trigger_identifier TEXT,
    conditions TEXT ,
    FOREIGN KEY (app_id) REFERENCES app_info(uid)
);


CREATE TABLE IF NOT EXISTS MergeResult.scenarios(
    scenario_name VARCHAR(128) ,
    app_id INT  NOT NULL,
    description VARCHAR(128) ,
    path VARCHAR(128),
    FOREIGN KEY (app_id) REFERENCES app_info(uid)
);




-- @author: Chen wenjie
-- @time: 2021-6-2 00:34
-- 配置用于存储merge后的数据的数据库
--
--
-- def get_res_model(self):  # 返回一个合并后的模型
--    res_model = Model()
--    res_model.set_id(self.app_id)
--    res_model.set_apk_name(self.app_apk_name)
--    res_model.set_package_name(self.app_package_name)
--    res_model.set_version(self.app_version)
--    res_model.state_list = self.res_state_list
--    res_model.transitions = self.res_transitions
--    res_model.states = self.res_states
--    return res_model
