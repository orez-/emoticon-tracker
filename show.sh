#! /bin/bash
psql -Atc "select encode(image, 'base64') from wp_slack.emoticon where ${1:-true} order by _row_created desc limit 1" | base64 -D
