import os

import requests

import model


class SlackError(Exception):
    """Error returned from Slack endpoint."""

    def __init__(self, response_json):
        self.json = response_json

    def __str__(self):
        return f"Bad Slack response: {self.json}"

    @classmethod
    def get_exc(cls, response_json):
        error = response_json.get('error')
        cls = next(
            (
                subcls
                for subcls in cls.__subclasses__()
                if getattr(subcls, 'slack_error', '') == error
            ),
            cls,
        )
        return cls(response_json)


class SlackAlreadyReactedError(SlackError):
    """already_reacted Slack error."""
    slack_error = "already_reacted"


class SlackTooManyReactionsError(SlackError):
    """too_many_reactions Slack error."""
    slack_error = "too_many_reactions"


def raise_for_slack_status(response):
    response.raise_for_status()
    response_json = response.json()
    if response_json.get('ok') is False:
        raise SlackError.get_exc(response_json)


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


def reply_to(original_message_payload, message):
    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        json={
            "channel": original_message_payload['channel'],
            "thread_ts": original_message_payload['ts'],
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
    try:
        raise_for_slack_status(response)
    except SlackAlreadyReactedError:
        return False
    return True


TOKEN = os.environ.get('SLACK_USER_TOKEN')
