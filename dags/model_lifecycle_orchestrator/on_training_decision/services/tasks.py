from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sdk import task, get_current_context
from kubernetes.client import models

from dags.model_lifecycle_orchestrator.on_training_decision.modules.schemas.airflow.configurations import TrainingDecisionCallbackConfigurations
from dags.model_lifecycle_orchestrator.on_training_decision.repositories.postgres.model_deployment_workflows import update_approved_training_workflow, delete_rejected_training_workflow
from dags.shared.modules.environment.ecr import ecr_environment
from dags.shared.modules.environment.k8s import k8s_environment

@task.branch(task_id="training_decision_callback")
def training_decision_callback() -> str:
    context = get_current_context()

    training_decision_callback_configurations = TrainingDecisionCallbackConfigurations.from_context(context)

    if training_decision_callback_configurations.approved:
        return update_approved_training_workflow.__name__
    else:
        return delete_rejected_training_workflow.__name__

def train_model() -> KubernetesPodOperator:
    return KubernetesPodOperator(
        task_id=train_model.__name__,
        name=train_model.__name__,
        namespace=k8s_environment.K8S_NAMESPACE,
        kubernetes_conn_id=k8s_environment.K8S_CONNECTION_ID,
        image=ecr_environment.TRAIN_MODEL_IMAGE,
        image_pull_policy="Always",
        image_pull_secrets=[
            models.V1LocalObjectReference(
                name=k8s_environment.K8S_DOCKER_REGISTRY_SECRET_NAME
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
        do_xcom_push=True,
        startup_timeout_seconds=300,
        get_logs=True,
        log_events_on_failure=True,
        on_finish_action="delete_pod",
    )