import json
import threading

from fastapi import APIRouter, Request
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler

from services.fraud_detection.src.services.airflow import trigger_airflow_dag
from services.fraud_detection.src.services.slack import update_message, common_callback_configurations
from shared.modules.environment import slack_environment

slack_app = App(
    token=slack_environment.SLACK_BOT_USER_AUTH_TOKEN,
    signing_secret=slack_environment.SLACK_SIGNING_SECRET
)
slack_handler = SlackRequestHandler(app=slack_app)

router = APIRouter(prefix="/slack", tags=["slack"])

@router.post("/events")
async def slack_events(request: Request):
    return await slack_handler.handle(request)

@slack_app.action("approve_training")
def approve_training(
    ack,
    body,
    action,
    client
):
    ack()
    data = json.loads(action["value"])
    trigger_airflow_dag(
        "train_callback",
        {
            "approved": True,
            "workflow_id": data["workflow_id"]
        }
    )
    update_message(
        client,
        body,
        f"✅ *Training approved* by @{body['user']['username']} — pipeline starting..."
    )

@slack_app.action("reject_training")
def reject_training(
    ack,
    body,
    action,
    client
):
    ack()
    data = json.loads(action["value"])
    trigger_airflow_dag(
        "train_callback",
        {
            "approved": False,
            "workflow_id": data["workflow_id"]
            **common_callback_configurations(body)
        }
    )
    update_message(
        client,
        body,
        f"❌ *Drift dismissed* by @{body['user']['username']}."
    )

@slack_app.action("approve_retraining")
def handle_approve_retraining(ack, body, client):
    ack()
    trigger_airflow_dag(
        "drift_approval_callback",
        {
            "approved": True,
            **common_callback_configurations(body)
        }
    )
    update_message(
        client,
        body,
        f"🔄 *Retraining approved* by @{body['user']['username']} — pipeline starting..."
    )



@slack_app.action("approve_promotion")
def handle_approve_promotion(ack, body, client):
    ack()
    trigger_airflow_dag(
        "promotion_callback",
        {
            "approved": True,
            **common_callback_configurations(body)
        }
    )
    update_message(
        client,
        body,
        f"🚀 *Promotion approved* by @{body['user']['username']} — promoting..."
    )

@slack_app.action("reject_promotion")
def handle_reject_promotion(ack, body, client):
    ack()
    trigger_airflow_dag(
        "promotion_callback",
        {
            "approved": False,
            **common_callback_configurations(body)
         }
    )
    update_message(
        client,
        body,
        f"❌ *Promotion rejected* by @{body['user']['username']}."
    )

def start_socket_mode() -> None:
    """Start Socket Mode in a daemon thread so it does not block FastAPI startup."""
    handler = SocketModeHandler(
        app=slack_app,
        app_token=slack_environment.SLACK_APP_LEVEL_TOKEN,
    )

    threading.Thread(
        target=handler.start,
        daemon=True,
        name="slack-socket-mode"
    ).start()