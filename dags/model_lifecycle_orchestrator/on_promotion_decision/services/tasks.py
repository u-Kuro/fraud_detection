import json

from airflow.sdk import task
from airflow.providers.http.operators.http import HttpOperator

from dags.model_lifecycle_orchestrator.on_promotion_decision.modules.schemas.airflow.configurations import PromotionDecisionCallbackConfigurations
from dags.model_lifecycle_orchestrator.on_promotion_decision.repositories.postgres.model_deployment_workflows import update_approved_promotion_workflow, delete_rejected_promotion_workflow

@task.branch(task_id="promotion_decision_callback")
def promotion_decision_callback(**context) -> str:
    promotion_decision_callback_configurations = PromotionDecisionCallbackConfigurations.from_context(context)

    if promotion_decision_callback_configurations.approved:
        return update_approved_promotion_workflow.__name__
    else:
        return delete_rejected_promotion_workflow.__name__

def apply_model_deployment() -> HttpOperator:
    # TODO - 26/07/2026 - Continue here... IDK how this works

    # need to do nektos/act call here to host instead for project simulation

    # But this is how it should be
    # return HttpOperator(
    #     task_id=apply_model_deployment.__name__,
    #     http_conn_id="github_api", # TODO - add in secretsmanager? airflow/connections/github_api
    #     endpoint=f"repos/{github_owner}/{github_repo}/actions/workflows/cd-fraud-detection.yaml/dispatches",
    #     method="POST",
    #     headers={
    #         "Authorization": "Bearer {{ var.value.github_token }}", # TODO - add in secretsmanager? airflow/variables/github_token
    #         "Accept": "application/vnd.github.v3+json",
    #     },
    #     data=json.dumps({
    #         "ref": "main",
    #         "inputs": {}
    #     }),
    #     response_check=lambda response: response.status_code == 204,
    # )