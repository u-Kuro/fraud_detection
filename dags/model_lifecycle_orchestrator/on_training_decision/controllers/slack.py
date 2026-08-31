import json
from uuid import UUID

from airflow.sdk import task

from dags.model_lifecycle_orchestrator.on_training_decision.modules.schemas.airflow.tasks import ModelDeploymentWorkflowForPromotion, TrainingDecision
from dags.model_lifecycle_orchestrator.on_training_decision.modules.schemas.airflow.xcom import TrainModelResult
from dags.shared.services.slack import slack_client, create_blocks
from dags.shared.modules.environment.slack import slack_environment

@task
def initialize_promotion_approval(train_model_result: TrainModelResult) -> ModelDeploymentWorkflowForPromotion:
    response = slack_client.chat_postMessage(
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=create_blocks(
            title="⚠️ Challenger Model Promotion Required",
            body=(
                f"Fraud Detection: {train_model_result.model_name} v{train_model_result.model_version} is ready.\n\n"
                
                f"• *F1-Score:* {train_model_result.model_f1_score:.4f}\n"
                f"• *PR-AUC:* {train_model_result.model_pr_auc:.4f}\n"
                f"• *Recall:* {train_model_result.model_recall:.4f}\n"
                f"• *Precision:* {train_model_result.model_precision:.4f}\n\n"
                
                "This approval request is initializing, please wait..."
            )
        )
    )
    slack_promotion_approval_message_ts = response["ts"]

    assert isinstance(slack_promotion_approval_message_ts, str)

    return ModelDeploymentWorkflowForPromotion(
        slack_promotion_approval_message_ts=slack_promotion_approval_message_ts
    )

def model_promotion_buttons(workflow_id: UUID) -> list:
    return [
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
                "text": "❌ Dismiss"
            },
            "style": "danger",
            "action_id": "reject_promotion",
            "value": json.dumps({
                "workflow_id": str(workflow_id)
            })
        },
    ]

@task
def update_promotion_approval(
    training_decision: TrainingDecision,
    train_model_result: TrainModelResult,
    model_deployment_workflow_for_promotion: ModelDeploymentWorkflowForPromotion,
):
    slack_client.chat_update(
        ts=model_deployment_workflow_for_promotion.slack_promotion_approval_message_ts,
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=create_blocks(
            title="⚠️ Challenger Model Promotion Required",
            body=(
                f"Fraud Detection: {train_model_result.model_name} v{train_model_result.model_version} is ready.\n\n"
                
                f"• *F1-Score:* {train_model_result.model_f1_score:.4f}\n"
                f"• *PR-AUC:* {train_model_result.model_pr_auc:.4f}\n"
                f"• *Recall:* {train_model_result.model_recall:.4f}\n"
                f"• *Precision:* {train_model_result.model_precision:.4f}\n\n"
                
                "Click Approve Promotion to promote to production."
            ),
            buttons=model_promotion_buttons(
                workflow_id=training_decision.model_deployment_workflow.id
            )
        )
    )