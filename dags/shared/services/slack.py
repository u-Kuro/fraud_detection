from airflow.providers.slack.hooks.slack import SlackHook
from slack_sdk import WebClient

from dags.shared.modules.environment.slack import slack_environment

slack_client: WebClient = SlackHook(slack_conn_id=slack_environment.SLACK_CONNECTION_ID).client

def create_blocks(title: str, body: str, buttons: list[dict] | None = None) -> list:
    blocks: list[dict[str, str | dict | list]] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": title
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": body
            }
        },
    ]
    if buttons:
        blocks.append({
            "type": "actions",
            "elements": buttons
        })
    return blocks