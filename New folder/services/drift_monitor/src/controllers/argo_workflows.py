import requests

from services.drift_monitor.src.modules.environment import environment
from services.shared.logging import logger

def submit_training_workflow(reason: str) -> None:
    """Submit an Argo Workflow for training_pipeline."""
    url = f"{environment.ARGO_SERVER_URL}/api/v1/workflows/{environment.ARGO_NAMESPACE}/submit"
    payload = {
        "resourceKind": "WorkflowTemplate",
        "resourceName": environment.ARGO_WORKFLOW_TEMPLATE_NAME,
        "submitOptions": {"labels": f"reason={reason}"},
    }
    headers = {}
    if environment.ARGO_TOKEN:
        headers["Authorization"] = f"Bearer {environment.ARGO_TOKEN}"
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        logger.info(f"Submitted training workflow: {resp.json().get('metadata', {}).get('name')}")
    except Exception as exc:
        logger.error(f"Failed to submit training workflow: {exc}", exc_info=True)