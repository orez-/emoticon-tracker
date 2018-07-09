import contextlib
import io
import os

import attr
import dateutil.parser
import requests
import sqlalchemy

import db

MANY_ADDED_THRESHOLD = 10


@attr.s(frozen=True)
class Emoticon:
    name = attr.ib()
    url = attr.ib()
    id = attr.ib(default=None, cmp=False)

    def row(self):
        image = _get_image(self.url)

        return {
            'name': self.name,
            'url': self.url,
            'image': image.raw_data,
            'added': image.created,
        }


@attr.s
class Image:
    raw_data = attr.ib()
    created = attr.ib()


class TooBig(ValueError):
    """Raised when the file is deemed to be too large to download."""


def stream_image(img_response):
    MAX_LENGTH = 1 * 1000 * 1000
    CHUNK_READ_SIZE = 1024  # arbitrary afaict

    data = io.BytesIO()
    content_length = img_response.headers.get('Content-Length')
    if content_length and int(content_length) > MAX_LENGTH:
        raise TooBig("Too big")

    size = 0
    for chunk in img_response.iter_content(CHUNK_READ_SIZE):
        size += len(chunk)
        if size > MAX_LENGTH:
            raise TooBig("Too big")

        data.write(chunk)
    return data


def _get_image(url):
    with contextlib.closing(requests.get(url, stream=True)) as img_response:
        last_modified = img_response.headers.get('Last-Modified')
        data = stream_image(img_response).getvalue()

    return Image(
        raw_data=data,
        created=dateutil.parser.parse(last_modified),
    )


def get_api(path, hipchat_org, token):
    if not path.startswith('https://'):
        path = f'https://{hipchat_org}.hipchat.com/{path}'
    response = requests.get(
        path,
        headers={'Authorization': f'Bearer {token}'},
    )
    if response.status_code == 401:
        print("Authentication error! Make sure you are using a valid HIPCHAT_TOKEN.")
        raise Exit
    response.raise_for_status()
    return response.json()


def get_api_items(path):
    """
    Yield a list of items from the hipchat api by path, respecting pagination.
    """
    while path:
        payload = get_api(
            path=path,
            hipchat_org=hipchat_org,
            token=token,
        )
        yield from payload['items']
        path = payload['links'].get('next')


def fetch_remote_emoticons():
    for emoticon_payload in get_api_items('v2/emoticon?type=group&max-results=1000'):
        yield Emoticon(
            name=emoticon_payload['shortcut'],
            url=emoticon_payload['url'],
        )


def fetch_local_emoticons():
    query = sqlalchemy.select([
        db.emoticon_table.c.id,
        db.emoticon_table.c.name,
        db.emoticon_table.c.url,
    ]).where(db.emoticon_table.removed.is_(None))
    return (
        Emoticon(
            id=row.id,
            name=row.name,
            url=row.url,
        ) for row in db.connection.execute(query)
    )


def add_emoticons(emoticons):
    if len(emoticons) >= MANY_ADDED_THRESHOLD:
        print("Fetching a LOT of images; this may take some time.")
    query = db.emoticon_table.insert().values([emoticon.row() for emoticon in emoticons])
    db.connection.execute(query)


def remove_emoticons(emoticons):
    emoticon_ids = [emoticon.id for emoticon in emoticons]
    query = (
        db.emoticon_table.update()
        .values({'removed': sqlalchemy.func.now()})
        .where(db.emoticon_table.c.id.in_(emoticon_ids))
    )
    db.connection.execute(query)


def _update_db_emoticons(db_emoticons, remote_emoticons):
    db_emoticons = set(db_emoticons)
    remote_emoticons = set(remote_emoticons)

    new_emoticons = remote_emoticons - db_emoticons
    removed_emoticons = db_emoticons - remote_emoticons

    add_emoticons(new_emoticons)
    remove_emoticons(removed_emoticons)


def update_db_emoticons():
    db_emoticons = fetch_local_emoticons()
    remote_emoticons = fetch_remote_emoticons()
    _update_db_emoticons(
        db_emoticons=db_emoticons,
        remote_emoticons=remote_emoticons,
    )


if __name__ == '__main__':
    token = os.environ.get('HIPCHAT_TOKEN')
    hipchat_org = os.environ.get('HIPCHAT_ORG')
    update_db_emoticons()
