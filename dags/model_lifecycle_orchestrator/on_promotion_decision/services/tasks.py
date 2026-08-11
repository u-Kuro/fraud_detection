import json

from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sdk import task, get_current_context
from airflow.providers.http.operators.http import HttpOperator
from kubernetes import client as k8s

from dags.model_lifecycle_orchestrator.on_promotion_decision.configs.airflow.data_keys import ArchiveKeys
from dags.model_lifecycle_orchestrator.on_promotion_decision.modules.schemas.airflow.configurations import PromotionDecisionCallbackConfigurations
from dags.model_lifecycle_orchestrator.on_promotion_decision.modules.schemas.airflow.xcom import ArchiveUsedTransactionInferencesXCom
from dags.model_lifecycle_orchestrator.on_promotion_decision.repositories.postgres.model_deployment_workflows import update_approved_promotion_workflow, delete_rejected_promotion_workflow
from dags.shared.modules.configs.airflow.airflow import AirflowConfig
from dags.shared.modules.configs.ecr import ECRConfig, ECRImageKeys, ECRSecretKeys
from dags.shared.modules.configs.github import GitHubConfig
from dags.shared.modules.configs.kubernetes import K8sConfig, K8sSecretKeys, K8sConfigMapKeys

@task.branch(task_id="promotion_decision_callback")
def promotion_decision_callback() -> str:
    context = get_current_context()

    promotion_decision_callback_configurations = PromotionDecisionCallbackConfigurations.from_context(context)

    if promotion_decision_callback_configurations.approved:
        return update_approved_promotion_workflow.__name__
    else:
        return delete_rejected_promotion_workflow.__name__

def apply_model_deployment() -> HttpOperator:
    return HttpOperator(
        task_id=apply_model_deployment.__name__,
        http_conn_id="github_api", # TODO - add in secretsmanager? airflow/connections/github_api
        endpoint=f"repos/{GitHubConfig.owner}/{GitHubConfig.repository}/actions/workflows/cd-fraud-detection.yaml/dispatches",
        method="POST",
        headers={
            "Authorization": "Bearer {{ var.value.github_token }}", # TODO - add in secretsmanager? airflow/variables/github_token
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

@task(task_id="archive_used_transaction_inferences")
def archive_used_transaction_inferences() -> None:
    context = get_current_context()
    archive_used_transaction_inferences_xcom = ArchiveUsedTransactionInferencesXCom.from_context(context)

    task_operator = KubernetesPodOperator(
        task_id=archive_used_transaction_inferences.__name__,
        name=archive_used_transaction_inferences.__name__,
        namespace=K8sConfig.namespace,
        image=f"{ECRConfig.ECR_URL}/{ECRImageKeys.archive}:latest",
        image_pull_policy="Always",
        image_pull_secrets=[
            k8s.V1LocalObjectReference(
                name=ECRSecretKeys.ecr_secret
            )
        ],
        env=[
            k8s.V1EnvVar(
                name=ArchiveKeys.TRANSACTION_INFERENCES_ARCHIVE_CUTOFF_ISO_DATETIME,
                value=archive_used_transaction_inferences_xcom.transaction_inferences_archive_cutoff_iso_datetime.isoformat()
            )
        ],
        env_from=[
            k8s.V1EnvFromSource(
                config_map_ref=k8s.V1ConfigMapEnvSource(
                    name=K8sConfigMapKeys.platform_infrastructure
                )
            ),
            k8s.V1EnvFromSource(
                secret_ref=k8s.V1SecretEnvSource(
                    name=K8sSecretKeys.mle_pipeline_secret
                )
            ),
        ],
        get_logs=True,
        is_delete_operator_pod=True,
        do_xcom_push=False,
        startup_timeout_seconds=300,
        config_file=AirflowConfig.kubeconfig_file_path
    )
    task_operator.execute(context=context)