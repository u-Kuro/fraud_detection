import json

from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.providers.http.operators.http import HttpOperator
from airflow.sdk import task, get_current_context
from kubernetes.client import models

from dags.model_lifecycle_orchestrator.on_promotion_decision.modules.configs.k8s.environments import ArchiveEnvironmentKeys
from dags.model_lifecycle_orchestrator.on_promotion_decision.modules.schemas.airflow.tasks import PromotionDecision, PromotedModelDeployment
from dags.model_lifecycle_orchestrator.on_promotion_decision.repositories.postgres.model_deployment_workflows import update_approved_promotion_workflow, delete_rejected_promotion_workflow
from dags.shared.modules.configs.github import GitHubConfig
from dags.shared.modules.environment.ecr import ecr_environment
from dags.shared.modules.environment.github import github_environment
from dags.shared.modules.environment.k8s import k8s_environment
from dags.shared.modules.schemas.airflow import TaskContext

@task
def get_promotion_decision() -> PromotionDecision:
    context = TaskContext(get_current_context())

    return context.configurations(pydantic_model=PromotionDecision)

@task.branch
def check_promotion_decision(promotion_decision: PromotionDecision) -> str:
    context = TaskContext(get_current_context())

    if promotion_decision.approved:
        return context.resolve_task_id(
            task_id=update_approved_promotion_workflow.__name__
        )
    else:
        return context.resolve_task_id(
            task_id=delete_rejected_promotion_workflow.__name__
        )

def apply_model_deployment() -> HttpOperator:
    return HttpOperator(
        task_id=apply_model_deployment.__name__,
        http_conn_id=github_environment.GITHUB_CONNECTION_ID,
        endpoint=f"repos/{GitHubConfig.owner}/{GitHubConfig.repository}/actions/workflows/cd-fraud-detection.yaml/dispatches",
        method="POST",
        headers={
            "Authorization": f"Bearer {github_environment.GITHUB_CONNECTION_ID}",
            "Accept": "application/vnd.github.v3+json",
        },
        # Data unused for nektos/act
        data=json.dumps({
            "ref": "main",
            "inputs": {
                "environment": "production"
            }
        }),
        response_check=lambda response: response.status_code == 204,
    )

@task
def archive_transaction_inferences_used_for_deployed_model(promoted_model_deployment: PromotedModelDeployment):
    return KubernetesPodOperator(
        task_id=archive_transaction_inferences_used_for_deployed_model.__name__,
        name=archive_transaction_inferences_used_for_deployed_model.__name__,
        namespace=k8s_environment.K8S_NAMESPACE,
        kubernetes_conn_id=k8s_environment.K8S_CONNECTION_ID,
        image=ecr_environment.ARCHIVE_IMAGE,
        image_pull_policy="Always",
        image_pull_secrets=[
            models.V1LocalObjectReference(
                name=k8s_environment.K8S_DOCKER_REGISTRY_SECRET_NAME
            )
        ],
        env=[
            models.V1EnvVar(
                name=ArchiveEnvironmentKeys.TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF,
                value=promoted_model_deployment.dataset_max_timestamp.isoformat()
            )
        ],
        env_from=[
            models.V1EnvFromSource(
                config_map_ref=models.V1ConfigMapEnvSource(
                    name=k8s_environment.K8S_BASE_CONFIG_MAP_NAME
                )
            ),
            models.V1EnvFromSource(
                secret_ref=models.V1SecretEnvSource(
                    name=k8s_environment.K8S_BASE_SECRET_NAME
                )
            ),
        ],
        do_xcom_push=False,
        startup_timeout_seconds=300,
        get_logs=True,
        log_events_on_failure=True,
        on_finish_action="delete_pod",
    )