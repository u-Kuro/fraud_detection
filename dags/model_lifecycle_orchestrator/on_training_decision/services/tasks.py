from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sdk import task, get_current_context, task_group
from kubernetes.client import models

from dags.model_lifecycle_orchestrator.on_training_decision.modules.schemas.airflow.xcom import TrainModelResult
from dags.model_lifecycle_orchestrator.on_training_decision.modules.schemas.airflow.tasks import TrainingDecision
from dags.model_lifecycle_orchestrator.on_training_decision.repositories.postgres.model_deployment_workflows import update_approved_training_workflow, delete_rejected_training_workflow
from dags.shared.modules.environment.ecr import ecr_environment
from dags.shared.modules.environment.k8s import k8s_environment
from dags.shared.modules.schemas.airflow import TaskContext
from dags.shared.modules.utilities.airflow.airflow import sequence

@task
def get_training_decision() -> TrainingDecision:
    context = TaskContext(get_current_context())

    return context.configurations(pydantic_model=TrainingDecision)

@task.branch
def check_training_decision(training_decision: TrainingDecision) -> str:
    context = TaskContext(get_current_context())

    if training_decision.approved:
        return context.resolve_task_id(
            task_id=update_approved_training_workflow.__name__
        )
    else:
        return context.resolve_task_id(
            task_id=delete_rejected_training_workflow.__name__
        )

def train_model_operator() -> KubernetesPodOperator:
    return KubernetesPodOperator(
        task_id=train_model_operator.__name__,
        name=train_model_operator.__name__,
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

@task_group
def train_model() -> TrainModelResult:
    @task
    def get_train_model_result() -> TrainModelResult:
        context = TaskContext(get_current_context())
        return context.xcom_pull(pydantic_model=TrainModelResult)

    sequence(
        train_model_operator(),
        train_model_result := get_train_model_result()
    )

    return train_model_result