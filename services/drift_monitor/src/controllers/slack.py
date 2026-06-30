import json
from uuid import uuid4, UUID

from slack_sdk.web.async_client import AsyncWebClient

from services.drift_monitor.src.repositories.postgres.model_deployment_workflows import create_train_pending_workflow, \
    update_training_approval_slack_ts
from shared.modules.environment import slack_environment
from shared.modules.schemas.model_deployment_workflow import ModelDeploymentWorkflow

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

async def post_cold_start_training_approval():
    workflow_id = uuid4()

    response = await client.chat_postMessage(
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=create_blocks(
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
                    "action_id": "approve_training",
                    "value": json.dumps({
                        "workflow_id": str(workflow_id)
                    })
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "❌ Dismiss"
                    },
                    "style": "danger",
                    "action_id": "reject_training",
                    "value": json.dumps({
                        "workflow_id": str(workflow_id)
                    })
                },
            ]
        )
    )

    create_train_pending_workflow(
        workflow_id=workflow_id,
        training_approval_slack_ts=response["ts"]
    )

async def post_training_approval(drift_summary: dict):
    workflow_id = uuid4()

    response = await client.chat_postMessage(
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=format_drift_blocks(drift_summary, workflow_id)
    )

    create_train_pending_workflow(
        workflow_id=workflow_id,
        training_approval_slack_ts=response["ts"]
    )

async def update_training_approval(drift_summary: dict, current_model_deployment_workflow: ModelDeploymentWorkflow):
    response = await client.chat_update(
        ts=current_model_deployment_workflow["training_approval_slack_ts"],
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=format_drift_blocks(drift_summary, current_model_deployment_workflow.id)
    )

    update_training_approval_slack_ts(response["ts"], current_model_deployment_workflow)

def format_drift_blocks(drift_summary: dict, workflow_id: UUID) -> list:
    dd = drift_summary.get("data_drift", {})
    cd = drift_summary.get("concept_drift", {})

    features_drift_text = (
        f"{dd.get('share_drifted_features', 0.0):.1%}" 
        f" {dd.get('number_of_drifted_features', 0)}" 
        f" / {dd.get('total_features', 0)}"
    )
    concept_drift_text = (
        f"{cd.get('f1_delta', 'n/a')} F1 Δ"
    )

    return create_blocks(
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
                "action_id": "approve_retraining",
                "value": json.dumps({
                    "workflow_id": str(workflow_id)
                })
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "❌ Dismiss"
                },
                "style": "danger",
                "action_id": "reject_retraining",
                "value": json.dumps({
                    "workflow_id": str(workflow_id)
                })
            },
        ]
    )