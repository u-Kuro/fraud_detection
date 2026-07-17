import json
from uuid import uuid4

from airflow.sdk import task

from dags.model_lifecycle_monitor.modules.schemas.airflow.xcom import PostRetrainingApprovalXCom, UpdateRetrainingPendingWorkflowXCom

from dags.shared.controllers.slack import slack_client, create_blocks
from dags.shared.modules.configs.airflow import ModelDeploymentWorkflowsKeys
from dags.shared.modules.environment.slack import slack_environment
from dags.shared.modules.schemas.airflow import AirflowTaskContext

@task(task_id="post_cold_start_training_approval")
def post_cold_start_training_approval(**context):
    workflow_id = str(uuid4())

    response = slack_client.chat_postMessage(
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
        )
    )

    training_approval_slack_ts = response["ts"]
    assert isinstance(training_approval_slack_ts, str)

    ti = AirflowTaskContext.from_context(context).ti
    ti.xcom_push(
        key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID_KEY,
        value=workflow_id
    )
    ti.xcom_push(
        key=ModelDeploymentWorkflowsKeys.TRAINING_APPROVAL_SLACK_TS_KEY,
        value=training_approval_slack_ts
    )

@task(task_id="post_retraining_approval")
def post_retraining_approval(**context):
    post_retraining_approval_xcom = PostRetrainingApprovalXCom.from_context(context)
    workflow_id = str(uuid4())

    response = slack_client.chat_postMessage(
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=format_retraining_approval_blocks(
            post_retraining_approval_xcom.drift_summary,
            workflow_id
        )
    )

    training_approval_slack_ts = response["ts"]
    assert isinstance(training_approval_slack_ts, str)

    ti = AirflowTaskContext.from_context(context).ti
    ti.xcom_push(
        key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID_KEY,
        value=workflow_id
    )
    ti.xcom_push(
        key=ModelDeploymentWorkflowsKeys.TRAINING_APPROVAL_SLACK_TS_KEY,
        value=training_approval_slack_ts
    )

@task(task_id="update_retraining_approval")
def update_retraining_approval(**context):
    update_retraining_approval_xcom = UpdateRetrainingPendingWorkflowXCom.from_context(context)

    response = slack_client.chat_update(
        ts=update_retraining_approval_xcom.training_approval_slack_ts,
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=format_retraining_approval_blocks(
            update_retraining_approval_xcom.drift_summary,
            update_retraining_approval_xcom.workflow_id
        )
    )

    training_approval_slack_ts = response["ts"]
    assert isinstance(training_approval_slack_ts, str)

    ti = AirflowTaskContext.from_context(context).ti
    ti.xcom_push(
        key=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID_KEY,
        value=update_retraining_approval_xcom.workflow_id
    )
    ti.xcom_push(
        key=ModelDeploymentWorkflowsKeys.TRAINING_APPROVAL_SLACK_TS_KEY,
        value=training_approval_slack_ts
    )

def format_retraining_approval_blocks(drift_summary: dict, workflow_id: str) -> list:
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
    )