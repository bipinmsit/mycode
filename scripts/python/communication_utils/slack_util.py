import requests
import json

SLACK_WEBHOOK = "https://hooks.slack.com/services/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"


def send_message(success, channel='photoscan', username='Chewbacca BOT', text=""):
    try:
        if success:
            icon_emoji = ':white_check_mark:'
            text = icon_emoji + ' ' + text
        else:
            icon_emoji = ':x:'
            text = icon_emoji + ' ' + text

        text = '____________________________\n' + text
        requests.post(
            url=SLACK_WEBHOOK,
            data=json.dumps({
                'channel': channel,
                'username': username,
                'text': text,
                'icon_url': 'https://www.shareicon.net/data/256x256/2016/11/21/854774_chewbacca_404x512.png'
            })
        )
    except Exception as e:
        pass
