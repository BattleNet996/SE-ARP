CREATE DATABASE IF NOT EXISTS AppRepo;

CREATE TABLE IF NOT EXISTS AppRepo.app_info(
    app_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    apk_name VARCHAR(128) NOT NULL,
    package_name VARCHAR(128) NOT NULL,
    version VARCHAR(32)
);

CREATE TABLE IF NOT EXISTS AppRepo.state(
    app_id INT UNSIGNED NOT NULL,
    state_id INT UNSIGNED NOT NULL,
    activity_name VARCHAR(128) NOT NULL
);

CREATE TABLE IF NOT EXISTS AppRepo.transition(
    transition_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    app_id INT UNSIGNED NOT NULL,
    source_state INT UNSIGNED NOT NULL,
    target_state INT UNSIGNED NOT NULL,
    trigger_action TEXT NOT NULL,
    trigger_identifier TEXT,
    conditions TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS AppRepo.scenarios(
    app_id INT UNSIGNED NOT NULL,
    scenario_name VARCHAR(128) NOT NULL,
    description VARCHAR(128) NOT NULL,
    path VARCHAR(128) NOT NULL
);
