CREATE DATABASE IF NOT EXISTS USERS;


CREATE TABLE IF NOT EXISTS USERS.user_info(
    uid VARCHAR(128) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    password VARCHAR(128) NOT NULL
);

CREATE TABLE IF NOT EXISTS USERS.user_email(
    uid VARCHAR(128) PRIMARY KEY,
    email VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS USERS.data_info(
    uid VARCHAR(128),
    app_name VARCHAR(128),
    time VARCHAR(128),
    file_path VARCHAR(128)
);


-- @author: Chen Wenjie, Wang Jiajie
-- @time: 2021-7-12 10:19
-- 配置用于存储用户信息与模型数据的数据库