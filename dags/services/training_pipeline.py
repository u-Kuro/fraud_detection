from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sdk import Variable
from kubernetes import client as k8s

from dags.modules.configs.dags import dags_config
from dags.modules.schemas.airflow import TrainingPipelineConfigurations

def run_training(**context) -> KubernetesPodOperator:
    configurations = TrainingPipelineConfigurations.from_context(context)
    return KubernetesPodOperator(
        task_id="run_training",
        name="training",
        namespace="default",
        image=f"{Variable.get("ecr_registry")}/training-pipeline:latest",
        image_pull_policy="Always",
        image_pull_secrets=[
            k8s.V1LocalObjectReference(
                name="ecr-secret"
            )
        ],
        env_vars=[
            k8s.V1EnvVar(
                name=dags_config.MODEL_DEPLOYMENT_WORKFLOW_ID_KEY,
                value=configurations.model_deployment_workflow_id
            ),
        ],
        env_from=[
            k8s.V1EnvFromSource(
                config_map_ref=k8s.V1ConfigMapEnvSource(
                    name="platform-infrastructure"
                )
            ),
            k8s.V1EnvFromSource(
                secret_ref=k8s.V1SecretEnvSource(
                    name="mle-pipeline-secret"
                )
            ),
        ],
        do_xcom_push=True,
        get_logs=True,
        is_delete_operator_pod=True,
        startup_timeout_seconds=300,
        config_file="/usr/local/airflow/dags/kubeconfig.yaml",
    )