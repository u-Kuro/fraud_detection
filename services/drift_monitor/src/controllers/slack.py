from pydantic import validate_call
from slack_sdk.web.async_client import AsyncWebClient
from services.drift_monitor.src.modules.environment import environment

client: AsyncWebClient = AsyncWebClient(token=environment.SLACK_BOT_USER_AUTH_TOKEN)

def blocks(title: str, body: str, buttons: list[dict] | None = None) -> list:
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

@validate_call(validate_return=True)
async def post_cold_start_notice_to_slack() -> str:
    """Posted once when no model has ever been deployed."""
    response = await client.chat_postMessage(
        channel=environment.SLACK_CHANNEL_ID,
        blocks=blocks(
            title="🆕 First Training Required",
            body=(
                "No model has been deployed yet. "
                "Click *Approve Training* to train the first model."
            ),
            buttons=[
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "✅ Approve Training"
                    },
                    "style": "primary",
                    "action_id": "approve_training"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "❌ Dismiss"
                    },
                    "style": "danger",
                    "action_id": "dismiss_drift"
                },
            ]
        )
    )

    return response["ts"]

@validate_call(validate_return=True)
async def post_drift_message(drift_summary: dict):
    """Post a drift message."""
    response = await client.chat_postMessage(
        channel=environment.SLACK_CHANNEL_ID,
        blocks=format_drift_blocks(drift_summary)
    )

    return response["ts"]

@validate_call(validate_return=True)
async def update_drift_message(drift_summary: dict, drift_slack_ts: str) -> str:
    """Update an existing drift message in place."""
    response = await client.chat_update(
        ts=drift_slack_ts,
        channel=environment.SLACK_CHANNEL_ID,
        blocks=format_drift_blocks(drift_summary)
    )

    return response["ts"]

def format_drift_blocks(drift_summary: dict) -> list:
    dd = drift_summary.get("data_drift", {})
    cd = drift_summary.get("concept_drift", {})

    features_drift_text = \
        f"{dd.get('share_drifted_features', 0.0):.1%}" \
        f" {dd.get('number_of_drifted_features', 0)}" \
        f" / {dd.get('total_features', 0)}"
    concept_drift_text = \
        f"{cd.get('f1_delta', 'n/a')} F1 Δ"

    return blocks(
        title="⚠️ Model Retraining Required",
        body=(
            "Significant data or concept drift has been detected in production.\n\n"
    
            f"• *Features drift:* {features_drift_text}\n"
            f"• *Concept drift:* {concept_drift_text}\n\n"

            " Click *Approve Retraining*  to kick off a new training run."
        ),
        buttons=[
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "🔄 Approve Retraining"
                },
                "style": "primary",
                "action_id": "approve_retraining"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "❌ Dismiss"
                },
                "style": "danger",
                "action_id": "dismiss_drift"
            },
        ]
    )