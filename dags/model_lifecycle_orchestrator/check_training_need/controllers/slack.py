import json
from uuid import UUID

from airflow.sdk import task

from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.tasks import ExpiredModelDeploymentWorkflowWithItsReplacement, ModelDeploymentWorkflowForTraining, DriftCheckResult
from dags.shared.services.slack import create_blocks, slack_client
from dags.shared.modules.environment.slack import slack_environment

@task
def invalidate_expired_promotion_approval(model_deployment_workflows: ExpiredModelDeploymentWorkflowWithItsReplacement | None) -> None:
    assert isinstance(model_deployment_workflows, ExpiredModelDeploymentWorkflowWithItsReplacement)

    slack_client.chat_update(
        ts=model_deployment_workflows.expired.promotion_approval_slack_ts,
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"~{(
                        "⚠️ Challenger Model Promotion Required"
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

@task
def invalidate_old_training_approval(
    model_deployment_workflow_for_training: ModelDeploymentWorkflowForTraining | None,
    drift_result: DriftCheckResult | None,
) -> None:
    assert model_deployment_workflow_for_training is not None
    assert model_deployment_workflow_for_training.training_approval_slack_ts is not None
    assert drift_result is not None

    slack_client.chat_update(
        ts=model_deployment_workflow_for_training.training_approval_slack_ts,
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"~{(
                        "⚠️ Model Retraining Required"
                        if drift_result.drift_detected
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
    drift_summary: dict[str, dict]
) -> list:
    data_drift = drift_summary.get("data_drift", {})
    concept_drift = drift_summary.get("concept_drift", {})

    share_drifted_features = data_drift.get("share_drifted_features")
    number_of_drifted_features = data_drift.get("number_of_drifted_features")
    total_features = data_drift.get("total_features")

    # Data Drift
    if (
        isinstance(share_drifted_features, float | int)
        and isinstance(number_of_drifted_features, float | int)
        and isinstance(total_features, float | int)
    ):
        features_drift_text = f"{share_drifted_features:.1%} ({number_of_drifted_features} / {total_features})"
    else:
        features_drift_text = "N/A"

    # Concept Drift
    f1_delta = concept_drift.get("f1_delta")
    if isinstance(f1_delta, float | int):
        concept_drift_text = f"{f1_delta:+.4f} F1 Δ"
    else:
        concept_drift_text = "N/A"

    return create_blocks(
        title="⚠️ Model Retraining Required",
        body=(
            "Significant data or concept drift has been detected in production.\n\n"

            f"• *Features drift:* {features_drift_text}\n"
            f"• *Concept drift:* {concept_drift_text}\n\n"

            "This approval request is initializing, please wait..."
        ),
    )

@task
def initialize_training_approval(
    model_deployment_workflow_for_training: ModelDeploymentWorkflowForTraining | None,
    drift_result: DriftCheckResult | None,
) -> ModelDeploymentWorkflowForTraining:
    assert model_deployment_workflow_for_training is not None
    assert drift_result is not None


    response = slack_client.chat_postMessage(
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=build_training_approval_blocks_initializing(
            drift_summary=drift_result.drift_summary
        )
    )
    training_approval_slack_ts = response["ts"]

    assert isinstance(training_approval_slack_ts, str)

    model_deployment_workflow_for_training.training_approval_slack_ts = training_approval_slack_ts

    return model_deployment_workflow_for_training

def cold_start_buttons(
    workflow_id: UUID,
    should_train_for_promotion: bool
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
                "should_train_for_promotion": should_train_for_promotion
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
                "should_train_for_promotion": should_train_for_promotion
            })
        },
    ]

def drift_retraining_buttons(
    workflow_id: UUID,
    should_train_for_promotion: bool
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
                "should_train_for_promotion": should_train_for_promotion
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
                "should_train_for_promotion": should_train_for_promotion
            })
        },
    ]

def build_training_approval_blocks(
    workflow_id: UUID,
    drift_summary: dict[str, dict] | None,
    should_train_for_promotion: bool,
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
                should_train_for_promotion=should_train_for_promotion
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
                should_train_for_promotion=should_train_for_promotion
            )
        )

@task
def update_training_approval(
    model_deployment_workflow_for_training: ModelDeploymentWorkflowForTraining,
    drift_result: DriftCheckResult | None,
) -> None:
    assert model_deployment_workflow_for_training.training_approval_slack_ts is not None
    assert model_deployment_workflow_for_training.workflow_id is not None
    assert drift_result is not None

    slack_client.chat_update(
        ts=model_deployment_workflow_for_training.training_approval_slack_ts,
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=build_training_approval_blocks(
            workflow_id=model_deployment_workflow_for_training.workflow_id,
            drift_summary=drift_result.drift_summary,
            should_train_for_promotion=model_deployment_workflow_for_training.should_train_for_promotion
        )
    )