import os

import requests

import model


def raise_for_slack_status(response):
    response.raise_for_status()
    response_json = response.json()
    if response_json.get('ok') is False:
        raise Exception(f"Bad Slack response: {response_json}")


def fetch_emoticons():
    response = requests.post(
        "https://slack.com/api/emoji.list",
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': f"Bearer {TOKEN}",
        }
    )
    raise_for_slack_status(response)
    for key, value in response.json()['emoji'].items():
        yield model.ComparableEmoticon(
            name=key,
            url=value,
        )


def send(channel, message):
    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        json={
            "channel": channel,
            "attachments": [
                {
                    "text": message,
                    "color": "#a256ed",
                }
            ]
        },
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': f"Bearer {TOKEN}",
        },
    )
    raise_for_slack_status(response)
    return response.json()


def react(original_message_payload, emoticon):
    response = requests.post(
        "https://slack.com/api/reactions.add",
        json={
            "name": emoticon,
            "channel": original_message_payload['channel'],
            "timestamp": original_message_payload['ts'],
        },
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': f"Bearer {TOKEN}",
        },
    )
    raise_for_slack_status(response)


TOKEN = os.environ.get('SLACK_USER_TOKEN')
