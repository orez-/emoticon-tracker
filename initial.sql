CREATE SCHEMA IF NOT EXISTS wp_hipchat;

CREATE TABLE wp_hipchat.emoticon (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    _row_created TIMESTAMP DEFAULT now() NOT NULL,
    added TIMESTAMP,
    removed TIMESTAMP,
    image BYTEA NOT NULL
);
