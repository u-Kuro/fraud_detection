import json
from uuid import UUID

from airflow.sdk import task, get_current_context

from dags.model_lifecycle_orchestrator.on_training_decision.modules.schemas.airflow.configurations import TrainingDecisionCallbackConfigurations
from dags.model_lifecycle_orchestrator.on_training_decision.modules.schemas.airflow.xcom import InitializePromotionApprovalXCom, UpdatePromotionApproval
from dags.shared.services.slack import slack_client, create_blocks
from dags.shared.modules.configs.airflow.data_keys import ModelDeploymentWorkflowsKeys
from dags.shared.modules.environment.slack import slack_environment
from dags.shared.modules.schemas.airflow import TaskContext

@task(task_id="initialize_promotion_approval")
def initialize_promotion_approval() -> None:
    context = get_current_context()

    initialize_promotion_approval_xcom = InitializePromotionApprovalXCom.from_context(context)

    response = slack_client.chat_postMessage(
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=create_blocks(
            title="⚠️ Challenger Model Promotion Required",
            body=(
                f"Fraud Detection: {initialize_promotion_approval_xcom.model_name} v{initialize_promotion_approval_xcom.model_version} is ready.\n\n"
                
                f"• *F1-Score:* {initialize_promotion_approval_xcom.f1_score:.4f}\n"
                f"• *PR-AUC:* {initialize_promotion_approval_xcom.pr_auc:.4f}\n"
                f"• *Recall:* {initialize_promotion_approval_xcom.recall:.4f}\n"
                f"• *Precision:* {initialize_promotion_approval_xcom.precision:.4f}\n\n"
                
                "This approval request is initializing, please wait..."
            )
        )
    )

    slack_promotion_approval_message_ts = response["ts"]
    assert isinstance(slack_promotion_approval_message_ts, str)

    ti = TaskContext.from_context(context).task_instance
    ti.xcom_push(
        key=ModelDeploymentWorkflowsKeys.SLACK_PROMOTION_APPROVAL_MESSAGE_TS,
        value=slack_promotion_approval_message_ts
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

@task(task_id="update_promotion_approval")
def update_promotion_approval() -> None:
    context = get_current_context()

    training_decision_callback_configurations = TrainingDecisionCallbackConfigurations.from_context(context)
    update_promotion_approval_xcom = UpdatePromotionApproval.from_context(context)

    slack_client.chat_update(
        ts=update_promotion_approval_xcom.slack_promotion_approval_message_ts,
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=create_blocks(
            title="⚠️ Challenger Model Promotion Required",
            body=(
                f"Fraud Detection: {update_promotion_approval_xcom.model_name} v{update_promotion_approval_xcom.model_version} is ready.\n\n"
                
                f"• *F1-Score:* {update_promotion_approval_xcom.f1_score:.4f}\n"
                f"• *PR-AUC:* {update_promotion_approval_xcom.pr_auc:.4f}\n"
                f"• *Recall:* {update_promotion_approval_xcom.recall:.4f}\n"
                f"• *Precision:* {update_promotion_approval_xcom.precision:.4f}\n\n"
                
                "Click Approve Promotion to promote to production."
            ),
            buttons=model_promotion_buttons(
                workflow_id=training_decision_callback_configurations.workflow_id
            )
        )
    )