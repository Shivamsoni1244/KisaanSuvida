-- ═══════════════════════════════════════════════════════════════════
--  Kisan Suvidha — MySQL Database Schema
--  Run: mysql -u root -p < kisan_schema.sql
-- ═══════════════════════════════════════════════════════════════════

CREATE DATABASE IF NOT EXISTS kisan_suvidha
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE kisan_suvidha;

-- ─── users ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(120)  NOT NULL,
    mobile        VARCHAR(15)   NOT NULL UNIQUE,
    state         VARCHAR(80)   DEFAULT '',
    district      VARCHAR(80)   DEFAULT '',
    sms_updates   TINYINT(1)    DEFAULT 0
                  COMMENT '1 = opted in for SMS crop alerts',
    lang          VARCHAR(5)    DEFAULT 'en'
                  COMMENT 'en | hi',
    registered_at DATETIME      DEFAULT CURRENT_TIMESTAMP,
    last_login    DATETIME      DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ─── crop_activities ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS crop_activities (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT           NOT NULL,
    activity_type   VARCHAR(30)   NOT NULL
                    COMMENT 'recommendation | analysis',

    -- common fields
    crop            VARCHAR(60)   NOT NULL,
    district        VARCHAR(80)   DEFAULT '',
    state           VARCHAR(80)   DEFAULT '',
    sms_sent        TINYINT(1)    DEFAULT 0
                    COMMENT '1 = SMS was dispatched for this activity',
    created_at      DATETIME      DEFAULT CURRENT_TIMESTAMP,

    -- recommendation-specific
    soil            VARCHAR(50)   DEFAULT '',
    season          VARCHAR(20)   DEFAULT '',
    confidence      VARCHAR(10)   DEFAULT ''
                    COMMENT 'HIGH | MEDIUM | LOW',
    temp            FLOAT         DEFAULT 0,
    humidity        FLOAT         DEFAULT 0,
    rainfall        FLOAT         DEFAULT 0,
    alternatives    TEXT
                    COMMENT 'JSON array of alternative crop names',

    -- analysis-specific
    analysis_status VARCHAR(20)   DEFAULT ''
                    COMMENT 'excellent | good | warning | danger',
    good_days       INT           DEFAULT 0,
    total_days      INT           DEFAULT 0,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ─── Useful indexes (Fixed for older MySQL versions) ──────────────────────────
CREATE INDEX idx_activities_user
    ON crop_activities(user_id);

CREATE INDEX idx_activities_type
    ON crop_activities(activity_type);

CREATE INDEX idx_activities_created
    ON crop_activities(created_at);


-- ─── Quick verification ───────────────────────────────────────────────────────
SHOW TABLES;