import json
from uuid import UUID

from airflow.sdk import task

from dags.model_lifecycle_orchestrator.modules.schemas.airflow.xcom import InitializeTrainingApprovalXCom, InvalidateOldTrainingApprovalXCom, UpdateTrainingApproval
from dags.shared.controllers.slack import create_blocks, slack_client
from dags.shared.modules.configs.airflow.data_keys import ModelDeploymentWorkflowsKeys
from dags.shared.modules.environment.slack import slack_environment
from dags.shared.modules.schemas.airflow import AirflowTaskContext

@task(task_id="invalidate_old_training_approval")
def invalidate_old_training_approval(**context) -> None:
    invalidate_old_training_approval_xcom = InvalidateOldTrainingApprovalXCom.from_context(context)

    slack_client.chat_update(
        ts=invalidate_old_training_approval_xcom.training_approval_slack_ts,
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"~{(
                        "⚠️ Model Retraining Required"
                        if invalidate_old_training_approval_xcom.drift_detected
                        else "🆕 First Training Required"
                    )}~"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🔄 Expired: a newer request will be issued."
                    }
                ]
            }
        ]
    )

def build_training_approval_blocks_initializing(
    drift_summary: dict[str, dict] | None,
) -> list:
    if drift_summary is None:
        return create_blocks(
            title="🆕 First Training Required",
            body=(
                "No model has been deployed yet. "
                "This approval request is initializing, please wait..."
            ),
        )
    else:
        data_drift = drift_summary.get("data_drift", {})
        concept_drift = drift_summary.get("concept_drift", {})

        features_drift_text = (
            f"{data_drift.get('share_drifted_features', 0.0):.1%}"
            f" {data_drift.get('number_of_drifted_features', 0)}"
            f" / {data_drift.get('total_features', 0)}"
        )
        concept_drift_text = f"{concept_drift.get('f1_delta', 'n/a')} F1 Δ"

        return create_blocks(
            title="⚠️ Model Retraining Required",
            body=(
                "Significant data or concept drift has been detected in production.\n\n"

                f"• *Features drift:* {features_drift_text}\n"
                f"• *Concept drift:* {concept_drift_text}\n\n"

                "This approval request is initializing, please wait..."
            ),
        )

@task(task_id="initialize_training_approval")
def initialize_training_approval(**context) -> None:
    initialize_training_approval_xcom = InitializeTrainingApprovalXCom.from_context(context)

    response = slack_client.chat_postMessage(
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=build_training_approval_blocks_initializing(
            drift_summary=initialize_training_approval_xcom.drift_summary
        )
    )

    training_approval_slack_ts = response["ts"]
    assert isinstance(training_approval_slack_ts, str)

    ti = AirflowTaskContext.from_context(context).ti
    ti.xcom_push(
        key=ModelDeploymentWorkflowsKeys.TRAINING_APPROVAL_SLACK_TS,
        value=training_approval_slack_ts
    )

def cold_start_buttons(
    workflow_id: UUID,
    for_promotion: bool
) -> list:
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
                "workflow_id": str(workflow_id),
                "for_promotion": for_promotion
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
                "workflow_id": str(workflow_id),
                "for_promotion": for_promotion
            })
        },
    ]

def drift_retraining_buttons(
    workflow_id: UUID,
    for_promotion: bool
) -> list:
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
                "workflow_id": str(workflow_id),
                "for_promotion": for_promotion
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
                "workflow_id": str(workflow_id),
                "for_promotion": for_promotion
            })
        },
    ]

def build_training_approval_blocks(
    workflow_id: UUID,
    drift_summary: dict[str, dict] | None,
    for_promotion: bool,
) -> list:
    if drift_summary is None:
        return create_blocks(
            title="🆕 First Training Required",
            body=(
                "No model has been deployed yet. "
                "Click *Approve Training* to train the first model."
            ),
            buttons=cold_start_buttons(
                workflow_id=workflow_id,
                for_promotion=for_promotion
            )
        )
    else:
        data_drift = drift_summary.get("data_drift", {})
        concept_drift = drift_summary.get("concept_drift", {})

        features_drift_text = (
            f"{data_drift.get('share_drifted_features', 0.0):.1%}"
            f" {data_drift.get('number_of_drifted_features', 0)}"
            f" / {data_drift.get('total_features', 0)}"
        )
        concept_drift_text = f"{concept_drift.get('f1_delta', 'n/a')} F1 Δ"

        return create_blocks(
            title="⚠️ Model Retraining Required",
            body=(
                "Significant data or concept drift has been detected in production.\n\n"

                f"• *Features drift:* {features_drift_text}\n"
                f"• *Concept drift:* {concept_drift_text}\n\n"

                "Click *Approve Retraining* to kick off a new training run."
            ),
            buttons=drift_retraining_buttons(
                workflow_id=workflow_id,
                for_promotion=for_promotion
            )
        )

@task(task_id="update_training_approval")
def update_training_approval(**context) -> None:
    update_training_approval_xcom = UpdateTrainingApproval.from_context(context)

    slack_client.chat_update(
        ts=update_training_approval_xcom.training_approval_slack_ts,
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=build_training_approval_blocks(
            workflow_id=update_training_approval_xcom.workflow_id,
            drift_summary=update_training_approval_xcom.drift_summary,
            for_promotion=update_training_approval_xcom.for_promotion
        )
    )