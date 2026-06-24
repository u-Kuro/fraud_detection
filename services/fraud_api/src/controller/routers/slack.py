import threading

import mlflow
from fastapi import APIRouter, Request
from mlflow import MlflowClient
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler
from sqlalchemy import text

from services.fraud_api.src.repositories.postgres import engine
from shared.configs import mlflow_config
from shared.environment import slack_environment

slack_app = App(
    token=slack_environment.SLACK_BOT_USER_AUTH_TOKEN,
    signing_secret=slack_environment.SLACK_SIGNING_SECRET
)

slack_handler: SlackRequestHandler = SlackRequestHandler(app=slack_app)
router = APIRouter(prefix="/slack", tags=["slack"])

@router.post("/events")
async def slack_events(request: Request):
    return await slack_handler.handle(request)

def set_training_approved(client, body) -> None:
    """Shared logic for approve_training and approve_retraining."""
    with engine.connect() as conn:
        conn.execute(text("""
            UPDATE pipeline_state
            SET training_approved = true
            WHERE state = 'drift_pending'
        """))
        conn.commit()
    client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        blocks=[{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"✅ *Training approved* pipeline starting..."
            },
        }],
    )


@slack_app.action("approve_training")
def handle_approve_training(ack, body, client, logger):
    ack()
    set_training_approved(client, body)

@slack_app.action("approve_retraining")
def handle_approve_retraining(ack, body, client, logger):
    ack()
    set_training_approved(client, body)

@slack_app.action("dismiss_drift")
def handle_dismiss_drift(ack, body, client, logger):
    ack()
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM pipeline_state"))
        conn.commit()
    client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        blocks=[{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"❌ *Drift dismissed*."
            },
        }],
    )

@slack_app.action("approve_promotion")
def handle_approve_promotion(ack, body, client, logger):
    ack()
    with engine.connect() as conn:
        conn.execute(text("""
            UPDATE pipeline_state
            SET promote_approved = true
            WHERE state = 'train_pending'
        """))
        conn.commit()
    client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        blocks=[{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"🚀 *Promotion approved* — promoting to production..."
            },
        }],
    )

@slack_app.action("reject_promotion")
def handle_reject_promotion(ack, body, client, logger):
    ack()
    # Read which MLflow candidate to clean up before deleting pipeline_state
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT model_version FROM pipeline_state
            WHERE state = 'train_pending'
            LIMIT 1
        """)).mappings().fetchone()
        conn.execute(text("DELETE FROM pipeline_state"))
        conn.commit()

    if row:
        try:
            mlflow.set_tracking_uri(mlflow_config.MLFLOW_TRACKING_URI)
            mc = MlflowClient()
            mc.delete_registered_model_alias("XGBoost", "candidate")
            mc.delete_model_version("XGBoost", str(row["model_version"]))
        except: pass

    client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        blocks=[{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"❌ *Promotion rejected*."
            },
        }],
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