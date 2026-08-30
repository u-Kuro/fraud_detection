from slack_bolt import Ack
from slack_sdk import WebClient

from services.fraud_detection.src.services.slack import slack_app
from services.fraud_detection.src.modules.schemas.slack import PromotionValue
from services.fraud_detection.src.services.mwaa import trigger_airflow_dag
from services.fraud_detection.src.services.idempotency import slack_action_store
from services.fraud_detection.src.services.slack import update_message

@slack_app.state("approve_promotion")
def approve_promotion(
    ack: Ack,
    body: dict,
    action: dict,
    client: WebClient
):
    ack()
    with slack_action_store.guard(action["action_id"], body["message"]["ts"]):
        promotion_value = PromotionValue.model_validate_json(action["value"])
        trigger_airflow_dag(
            dag_id="on_promotion_decision",
            configurations={
                "approved": True,
                "workflow_id": str(promotion_value.workflow_id),
            }
        )
        update_message(
            client=client,
            body=body,
            text_markdown=f"🚀 *Promotion approved* by @{body['user']['username']}, added to queue..."
        )

@slack_app.state("reject_promotion")
def reject_promotion(
    ack,
    body,
    action,
    client
):
    ack()
    with slack_action_store.guard(action["action_id"], body["message"]["ts"]):
        promotion_value = PromotionValue.model_validate_json(action["value"])
        trigger_airflow_dag(
            dag_id="on_promotion_decision",
            configurations={
                "approved": False,
                "workflow_id": str(promotion_value.workflow_id),
             }
        )
        update_message(
            client=client,
            body=body,
            text_markdown=f"❌ *Promotion dismissed* by @{body['user']['username']}."
        )