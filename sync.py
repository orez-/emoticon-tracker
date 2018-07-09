import db
import hipchat


def _update_db_emoticons(db_emoticons, remote_emoticons):
    db_emoticons = set(db_emoticons)
    remote_emoticons = set(remote_emoticons)

    new_emoticons = remote_emoticons - db_emoticons
    removed_emoticons = db_emoticons - remote_emoticons

    db.add_emoticons(new_emoticons)
    db.remove_emoticons(removed_emoticons)


def update_db_emoticons():
    db_emoticons = db.fetch_emoticons()
    remote_emoticons = hipchat.fetch_emoticons()
    _update_db_emoticons(
        db_emoticons=db_emoticons,
        remote_emoticons=remote_emoticons,
    )


if __name__ == '__main__':
    update_db_emoticons()
