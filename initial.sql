CREATE SCHEMA IF NOT EXISTS wp_slack;

CREATE TABLE wp_slack.emoticon (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    _row_created TIMESTAMP DEFAULT now() NOT NULL,
    added TIMESTAMP,
    removed TIMESTAMP,
    image BYTEA,
    added_by TEXT
);
