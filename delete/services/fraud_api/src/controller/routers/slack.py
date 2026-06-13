from fastapi import APIRouter, Request
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler

from services.fraud_api.src.modules.environment import environment

slack_app = App(
    token=environment.SLACK_BOT_USER_AUTH_TOKEN,
    signing_secret=environment.SLACK_SIGNING_SECRET
)

slack_handler: SlackRequestHandler = SlackRequestHandler(app=slack_app)
router = APIRouter(prefix="/slack", tags=["slack"])

@router.post("/events")
async def slack_events(request: Request):
    return await slack_handler.handle(request)

@slack_app.action("approve_training")
def handle_approve(ack, body, respond):
    ack()
    user = body["user"]["username"]
    respond(f"✅ Request approved by @{user}!", replace_original=True)

@slack_app.action("dismiss_drift")
def handle_approve(ack, body, respond):
    ack()
    user = body["user"]["username"]
    respond(f"✅ Request approved by @{user}!", replace_original=True)

handler = SocketModeHandler(app=slack_app, app_token=environment.SLACK_APP_LEVEL_TOKEN)
handler.start()