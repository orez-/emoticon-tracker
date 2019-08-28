import datetime
import os.path

import dateutil.parser
import pytz

import db
import slack
import sync

REMOVED = True
ADDED = False

MAX_REPLIES = 50
MAX_REACTIONS = 20

_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
ANNOUNCEMENT_FILE = os.path.join(_SCRIPT_DIR, '.last_announcement')
_numbers = {
    1: 'one',
    2: 'two',
    3: 'three',
    4: 'four',
    5: 'five',
    6: 'six',
    7: 'seven',
    8: 'eight',
    9: 'nine',
    10: 'ten',
}


def log_last_announcement(announcement_time):
    with open(ANNOUNCEMENT_FILE, 'w') as file:
        file.write(announcement_time.isoformat())


def get_last_announcement_time():
    try:
        with open(ANNOUNCEMENT_FILE, 'r') as file:
            last_time = file.read()
    except IOError:
        return None

    return dateutil.parser.parse(last_time)


def _example_emoticons(emoticons):
    assert emoticons
    display_emoticons = ' and '.join(map(':{0.name}:'.format, emoticons[:2]))
    if len(emoticons) <= 2:
        return display_emoticons
    return f"including {display_emoticons}"


def get_change_message(changes):
    is_are = "is" if len(changes.get(ADDED) or changes.get(REMOVED)) == 1 else 'are'
    clauses = []
    if ADDED in changes:
        emoticons = changes[ADDED]
        count = len(emoticons)
        number = _numbers.get(count, count)
        plural = '' if count == 1 else 's'
        clauses.append(f"{number} new emoticon{plural} ({_example_emoticons(emoticons)})")
    if REMOVED in changes:
        emoticons = changes[REMOVED]
        count = len(emoticons)
        number = _numbers.get(count, count)
        plural = '' if count == 1 else 's'
        clauses.append(f"{number} removed emoticon{plural} ({_example_emoticons(emoticons)})")
    clauses = ', and '.join(clauses)
    return f"Hello! There {is_are} {clauses}."


def announce_changes():
    sync.update_db_emoticons()
    # get now as soon as possible after syncing
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

    last_time = get_last_announcement_time()
    if not last_time:
        print("No previous announcement time; setting to now and exiting.")
        log_last_announcement(now)
        return

    changes = db.get_changes_since(last_time)
    if not changes:
        print("No changes")
        return

    message = get_change_message(changes)
    message_payload = slack.send('#emoticon-requests', message)
    slack.reply_to(
        message_payload, ''.join(map(":{0.name}:".format, changes[ADDED][:MAX_REPLIES]))
    )

    log_last_announcement(now)
    print(message)


if __name__ == '__main__':
    announce_changes()
