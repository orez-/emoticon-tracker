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
    for emoticon_payload in _get_api_items('v2/emoticon?type=group&max-results=1000'):
        yield model.Emoticon(
            name=emoticon_payload['shortcut'],
            url=emoticon_payload['url'],
        )


token = os.environ.get('HIPCHAT_TOKEN')
hipchat_org = os.environ.get('HIPCHAT_ORG')
