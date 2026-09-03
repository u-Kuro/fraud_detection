import threading

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

from services.shared.src.modules.environment.slack import slack_environment

slack_app = App(
    token=slack_environment.SLACK_BOT_TOKEN,
    signing_secret=slack_environment.SLACK_SIGNING_SECRET
)

def start_socket_mode() -> None:
    handler = SocketModeHandler(
        app=slack_app,
        app_token=slack_environment.SLACK_APP_TOKEN,
    )

    threading.Thread(
        target=handler.start,
        daemon=True,
        name="slack_socket_mode"
    ).start()

def update_message(client: WebClient, body: dict, text_markdown: str) -> None:
    client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        blocks=[{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text_markdown
            }
        }],
    )

def common_callback_configurations(body: dict) -> dict:
    return {
        "approved_by": body.get("user", {}).get("username"),
        "channel_id": body.get("channel", {}).get("id"),
        "message_ts": body.get("message", {}).get("ts"),
    }