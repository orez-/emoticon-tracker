import collections
import datetime

import db
import slack


Changes = collections.namedtuple('Changes', 'added removed')


def _update_db_emoticons(db_emoticons, remote_emoticons):
    db_emoticons = set(db_emoticons)
    remote_emoticons = set(remote_emoticons)

    new_emoticons = remote_emoticons - db_emoticons
    removed_emoticons = db_emoticons - remote_emoticons

    added = db.add_emoticons(new_emoticons)
    removed = db.remove_emoticons(removed_emoticons)
    return Changes(
        added=added,
        removed=removed,
    )


def update_db_emoticons():
    db_emoticons = db.fetch_emoticons()
    remote_emoticons = slack.fetch_emoticons()
    return _update_db_emoticons(
        db_emoticons=db_emoticons,
        remote_emoticons=remote_emoticons,
    )


if __name__ == '__main__':
    added, removed = update_db_emoticons()
    print(datetime.datetime.now(), "added:", added, "; removed:", removed)
