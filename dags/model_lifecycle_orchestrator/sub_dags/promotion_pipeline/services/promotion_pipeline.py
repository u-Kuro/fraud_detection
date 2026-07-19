from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes import client as k8s

from dags.model_lifecycle_orchestrator.sub_dags.promotion_pipeline.modules.schemas.airflow.configurations import PromotionPipelineConfigurations

from dags.shared.modules.configs import ecr_config
from dags.shared.modules.configs.airflow import ModelDeploymentWorkflowsKeys

def run_promotion(**context) -> KubernetesPodOperator:
    configurations = PromotionPipelineConfigurations.from_context(context)
    return KubernetesPodOperator(
        task_id="run_promotion",
        name="promotion",
        namespace="default",
        # TODO - no promotion-pipeline in platform-gitops infra i think?
        image=f"{ecr_config.ECR_URL}/promotion-pipeline:latest",
        image_pull_policy="Always",
        image_pull_secrets=[
            k8s.V1LocalObjectReference(
                name="ecr-secret"
            )
        ],
        env_vars=[
            k8s.V1EnvVar(
                name=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID_KEY,
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