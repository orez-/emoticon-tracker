import contextlib
import io

import attr
import dateutil.parser
import requests


@attr.s(frozen=True)
class ComparableEmoticon:
    """
    Partial emoticon data which compares equivalent on only name and url.
    """
    name = attr.ib()
    url = attr.ib()
    id = attr.ib(default=None, cmp=False)
    added_by = attr.ib(default=None, cmp=False)


@attr.s
class Image:
    raw_data = attr.ib()
    created = attr.ib()


class TooBig(ValueError):
    """Raised when the file is deemed to be too large to download."""


def _stream_image(img_response):
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


def get_image(url):
    with contextlib.closing(requests.get(url, stream=True)) as img_response:
        last_modified = img_response.headers.get('Last-Modified')
        data = _stream_image(img_response).getvalue()

    return Image(
        raw_data=data,
        created=dateutil.parser.parse(last_modified) if last_modified else None,
    )
