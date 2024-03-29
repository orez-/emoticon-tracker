import os

import requests

import model


def _get_api(path, hipchat_org, token):
    if not path.startswith('https://'):
        path = f'https://{hipchat_org}.hipchat.com/{path}'
    response = requests.get(
        path,
        headers={'Authorization': f'Bearer {token}'},
    )
    if response.status_code == 401:
        print("Authentication error! Make sure you are using a valid HIPCHAT_TOKEN.")
        raise Exception
    response.raise_for_status()
    return response.json()


def _get_api_items(path):
    """
    Yield a list of items from the hipchat api by path, respecting pagination.
    """
    while path:
        payload = _get_api(
            path=path,
            hipchat_org=hipchat_org,
            token=token,
        )
        yield from payload['items']
        path = payload['links'].get('next')


def fetch_emoticons():
    for emoticon_payload in _get_api_items('v2/emoticon?type=group&max-results=1000&expand=items'):
        yield model.ComparableEmoticon(
            name=emoticon_payload['shortcut'],
            url=emoticon_payload['url'],
            added_by=emoticon_payload['creator']['name'] if emoticon_payload['creator'] else None,
        )


def send(room, message):
    path = f'/v2/room/{room}/notification'
    if not path.startswith('https://'):
        path = f'https://{hipchat_org}.hipchat.com/{path}'
    response = requests.post(
        path,
        json=message,
        headers={'Authorization': f'Bearer {talk_token}'},
    )
    if response.status_code == 401:
        print("Authentication error! Make sure you are using a valid HIPCHAT_TALK_TOKEN.")
        raise Exception
    response.raise_for_status()


token = os.environ.get('HIPCHAT_TOKEN')
talk_token = os.environ.get('HIPCHAT_TALK_TOKEN')
hipchat_org = os.environ.get('HIPCHAT_ORG')
