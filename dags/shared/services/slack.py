from airflow.providers.slack.hooks.slack import SlackHook
from airflow.sdk import get_current_context
from slack_sdk import WebClient

from dags.shared.modules.environment.slack import slack_environment
from dags.shared.modules.schemas.airflow import TaskContext

slack_client: WebClient = SlackHook(slack_conn_id=slack_environment.SLACK_CONNECTION_ID).client

def slack_failure_alert():
    context = TaskContext(get_current_context())
    ti = context.task_instance
    slack_client.chat_postMessage(
        channel=slack_environment.SLACK_CHANNEL_ID,
        blocks=create_blocks(
            title="⚠️ Task Failed",
            body=(
                f"DAG: `{ti.dag_id}`\n\n"
                
                f"• *Task:* `{ti.task_id}`\n"
                f"• *Run:* `{ti.run_id}`\n"
                f"• *Error:* `{context.exception or 'N/A'}`\n\n"
                
                f"<{ti.log_url}|View Workflow Run>"
            )
        )
    )

def create_blocks(title: str, body: str, buttons: list[dict] | None = None) -> list:
    blocks: list[dict[str, str | dict | list]] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": title
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": body
            }
        },
    ]
    if buttons:
        blocks.append({
            "type": "actions",
            "elements": buttons
        })
    return blocks