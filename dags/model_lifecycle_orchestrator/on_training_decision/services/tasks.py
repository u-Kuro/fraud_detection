from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sdk import task
from kubernetes import client as k8s

from dags.model_lifecycle_orchestrator.on_training_decision.modules.schemas.airflow.configurations import TrainingDecisionCallbackConfigurations

from dags.model_lifecycle_orchestrator.on_training_decision.repositories.postgres.model_deployment_workflows import update_approved_training_workflow, delete_rejected_training_workflow
from dags.shared.modules.configs.airflow.airflow import AirflowConfig
from dags.shared.modules.configs.ecr import ECRConfig, ECRImageKeys, ECRSecretKeys
from dags.shared.modules.configs.kubernetes import K8sConfig, K8sConfigMapKeys, K8sSecretKeys

@task.branch(task_id="training_decision_callback")
def training_decision_callback(**context) -> str:
    training_decision_callback_configurations = TrainingDecisionCallbackConfigurations.from_context(context)

    if training_decision_callback_configurations.approved:
        return update_approved_training_workflow.__name__
    else:
        return delete_rejected_training_workflow.__name__

def train_model() -> KubernetesPodOperator:
    return KubernetesPodOperator(
        task_id=train_model.__name__,
        name=train_model.__name__,
        namespace=K8sConfig.namespace,
        image=f"{ECRConfig.ECR_URL}/{ECRImageKeys.train_model}:latest",
        image_pull_policy="Always",
        image_pull_secrets=[
            k8s.V1LocalObjectReference(
                name=ECRSecretKeys.ecr_secret
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
        do_xcom_push=True,
        startup_timeout_seconds=300,
        config_file=AirflowConfig.kubeconfig_file_path
    )