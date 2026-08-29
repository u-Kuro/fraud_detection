from slack_bolt import Ack
from slack_sdk import WebClient

from services.fraud_detection.src.services.slack import slack_app
from services.fraud_detection.src.modules.schemas.slack import TrainingValue
from services.fraud_detection.src.services.mwaa import trigger_airflow_dag
from services.fraud_detection.src.services.idempotency import slack_action_store
from services.fraud_detection.src.services.slack import update_message

@slack_app.action("approve_retraining")
def approve_retraining(
    ack: Ack,
    body: dict,
    action: dict,
    client: WebClient
):
    ack()
    with slack_action_store.guard(action["action_id"], body["message"]["ts"]):
        training_value = TrainingValue.model_validate_json(action["value"])
        trigger_airflow_dag(
            dag_id="on_training_decision",
            configurations={
                "approved": True,
                "workflow_id": str(training_value.workflow_id),
                "for_promotion": training_value.for_promotion
            }
        )
        update_message(
            client=client,
            body=body,
            text_markdown=f"🔄 *Retraining approved* by @{body['user']['username']}, added to queue..."
        )

@slack_app.action("reject_retraining")
def reject_retraining(
    ack: Ack,
    body: dict,
    action: dict,
    client: WebClient
):
    ack()
    with slack_action_store.guard(action["action_id"], body["message"]["ts"]):
        training_value = TrainingValue.model_validate_json(action["value"])
        trigger_airflow_dag(
            dag_id="on_training_decision",
            configurations={
                "approved": False,
                "workflow_id": str(training_value.workflow_id),
                "for_promotion": training_value.for_promotion
            }
        )
        update_message(
            client=client,
            body=body,
            text_markdown=f"❌ *Retraining dismissed* by @{body['user']['username']}."
        )