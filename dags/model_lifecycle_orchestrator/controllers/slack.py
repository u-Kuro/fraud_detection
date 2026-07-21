import json

from airflow.sdk import task

from dags.shared.controllers.slack import create_blocks, slack_client
from dags.shared.modules.configs.airflow.data_keys import ModelDeploymentWorkflowsKeys
from dags.shared.modules.environment.slack import slack_environment
from dags.shared.modules.schemas.airflow import AirflowTaskContext

def cold_start_buttons(workflow_id: str) -> list:
    return [
        {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "✅ Approve Training"
            },
            "style": "primary",
            "action_id": "approve_training",
            "value": json.dumps({
                "workflow_id": workflow_id
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
                "workflow_id": workflow_id
            })
        },
    ]


def drift_retraining_buttons(workflow_id: str) -> list:
    return [
        {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "🔄 Approve Retraining"
            },
            "style": "primary",
            "action_id": "approve_retraining",
            "value": json.dumps({
                "workflow_id": workflow_id
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
                "workflow_id": workflow_id
            })
        },
    ]


def build_training_approval_blocks(
    workflow_id: str,
    drift_summary: dict | None,
    with_buttons: bool
) -> list:
    if drift_summary is not None:
        data_drift = drift_summary.get("data_drift", {})
        concept_drift = drift_summary.get("concept_drift", {})

        features_drift_text = (
            f"{data_drift.get('share_drifted_features', 0.0):.1%}"
            f" {data_drift.get('number_of_drifted_features', 0)}"
            f" / {data_drift.get('total_features', 0)}"
        )
        concept_drift_text = (
            f"{concept_drift.get('f1_delta', 'n/a')} F1 Δ"
        )

        return create_blocks(
            title="⚠️ Model Retraining Required",
            body=(
                "Significant data or concept drift has been detected in production.\n\n"
                
                f"• *Features drift:* {features_drift_text}\n"
                f"• *Concept drift:* {concept_drift_text}\n\n"
                
                "Click *Approve Retraining* to kick off a new training run."
            ),
            buttons=drift_retraining_buttons(workflow_id) if with_buttons else None
        )
    else:
        return create_blocks(
            title="🆕 First Training Required",
            body=(
                "No model has been deployed yet. "
                "Click *Approve Training* to train the first model."
            ),
            buttons=cold_start_buttons(workflow_id) if with_buttons else None
        )


@task(task_id="invalidate_old_training_approval")
def invalidate_old_training_approval(**context) -> None:
    title = "🆕 First Training Required" if drift_summary else "⚠️ Model Retraining Required"

    slack_client.chat_update(
        ts=training_approval_slack_ts,
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"~{title}~"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🔄 Superseded — a newer request has been issued."
                    }
                ]
            }
        ]
    )


@task(task_id="initialize_training_approval")
def initialize_training_approval(**context) -> None:

    response = slack_client.chat_postMessage(
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=build_training_approval_blocks(
            workflow_id,
            drift_summary,
            with_buttons=False
        )
    )

    training_approval_slack_ts = response["ts"]
    assert isinstance(training_approval_slack_ts, str)

    ti = AirflowTaskContext.from_context(context).ti
    ti.xcom_push(
        key=ModelDeploymentWorkflowsKeys.TRAINING_APPROVAL_SLACK_TS,
        value=training_approval_slack_ts
    )


@task(task_id="update_training_approval")
def update_training_approval(**context) -> None:

    slack_client.chat_update(
        ts=training_approval_slack_ts,
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=build_training_approval_blocks(
            workflow_id,
            drift_summary,
            with_buttons=True
        )
    )