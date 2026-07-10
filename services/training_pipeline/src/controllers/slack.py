import json
from uuid import UUID

from slack_sdk.web.async_client import AsyncWebClient

from services.training_pipeline.src.modules.schemas import ModelDeploymentWorkflow
from services.training_pipeline.src.repositories.postgres.model_deployment_workflows import \
    update_promotion_approval_slack_ts
from services.shared.modules.environment import slack_environment

client: AsyncWebClient = AsyncWebClient(token=slack_environment.SLACK_BOT_USER_AUTH_TOKEN)

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

async def update_promotion_approval(
    model_name: str,
    model_version: int,
    model_metrics: dict[str, float],
    model_deployment_workflow: ModelDeploymentWorkflow,
):
    response = await client.chat_update(
        ts=model_deployment_workflow.promotion_approval_slack_ts,
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=format_promotion_approval_blocks(
            model_name,
            model_version,
            model_metrics,
            model_deployment_workflow.id,
        )
    )

    update_promotion_approval_slack_ts(
        id=model_deployment_workflow.id,
        promotion_approval_slack_ts=response["ts"]
    )

def format_promotion_approval_blocks(
    model_name: str,
    model_version: int,
    model_metrics: dict[str, float],
    workflow_id: UUID,
) -> list:
    return create_blocks(
        title="⚠️ Model Promotion Required",
        body=(
            f"Model `{model_name}` v{model_version} is ready.\n"
            f"F1: `{model_metrics['f1']:.4f}` | ROC-AUC: `{model_metrics['roc_auc']:.4f}`\n\n"
            
            "Approve to promote to production."
        ),
        buttons=[
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "🚀 Approve Promotion"
                },
                "style": "primary",
                "action_id": "approve_promotion",
                "value": json.dumps({
                    "workflow_id": str(workflow_id)
                })
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "❌ Reject"
                },
                "style": "danger",
                "action_id": "reject_promotion",
                "value": json.dumps({
                    "workflow_id": str(workflow_id)
                })
            }
        ]
    )