CREATE DATABASE IF NOT EXISTS APPREPO;

CREATE DATABASE IF NOT EXISTS APPREPO;

CREATE TABLE IF NOT EXISTS APPREPO.app_info(
    app_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    apk_name VARCHAR(128) NOT NULL,
    package_name VARCHAR(128) NOT NULL,
    version VARCHAR(32) NOT NULL,
    author VARCHAR(32)
);

CREATE TABLE IF NOT EXISTS APPREPO.state(
    app_id INT UNSIGNED NOT NULL,
    state_id INT UNSIGNED NOT NULL PRIMARY KEY,
    activity_name VARCHAR(128) NOT NULL,
    screen_shot mediumblob NOT NULL,
    layout LONGTEXT NOT NULL , 
    FOREIGN KEY (app_id) REFERENCES app_info(uid)
);

CREATE TABLE IF NOT EXISTS APPREPO.transition(
    transition_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    app_id INT UNSIGNED NOT NULL,
    source_state INT UNSIGNED NOT NULL,
    target_state INT UNSIGNED NOT NULL,
    trigger_action TEXT NOT NULL,
    trigger_identifier TEXT,
    conditions TEXT ,
    FOREIGN KEY (app_id) REFERENCES app_info(uid)
);

CREATE TABLE IF NOT EXISTS APPREPO.scenarios(
    app_id INT UNSIGNED NOT NULL,
    scenario_name VARCHAR(128) NOT NULL,
    description VARCHAR(128) NOT NULL,
    path VARCHAR(128) NOT NULL ,
    FOREIGN KEY (app_id) REFERENCES app_info(uid)
);