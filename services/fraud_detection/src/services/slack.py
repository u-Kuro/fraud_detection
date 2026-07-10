from services.shared import logger

def update_message(client, body: dict, text_markdown: str) -> None:
    try:
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
    except Exception as exc:
        logger.warning(f"Slack message update failed (non-fatal): {exc}")

def common_callback_configurations(body: dict) -> dict:
    return {
        "approved_by": body.get("user", {}).get("username"),
        "channel_id": body.get("channel", {}).get("id"),
        "message_ts": body.get("message", {}).get("ts"),
    }