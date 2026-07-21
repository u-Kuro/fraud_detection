from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sdk import task
from kubernetes import client as k8s

from dags.model_lifecycle_orchestrator.modules.schemas.airflow.xcom import HasDriftXCom
from dags.shared.modules.configs.airflow.data_keys import DriftMonitorKeys
from dags.shared.modules.configs.ecr import ECRConfig
from dags.shared.modules.schemas.airflow import AirflowTaskContext

drift_check_task_id = "drift_check"
drift_check = KubernetesPodOperator(
    task_id=drift_check_task_id,
    name=drift_check_task_id,
    namespace="default",
    image=f"{ECRConfig.ECR_URL}/drift-check:latest",
    image_pull_policy="Always",
    image_pull_secrets=[
        k8s.V1LocalObjectReference(
            name="ecr-secret"
        )
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
    get_logs=True,
    is_delete_operator_pod=True,
    do_xcom_push=True,
    startup_timeout_seconds=120,
    config_file="/usr/local/airflow/dags/kubeconfig.yaml",
)

@task.branch(task_id="has_drift")
def has_drift(**context):
    has_drift_xcom = HasDriftXCom.from_context(context)

    ti = AirflowTaskContext.from_context(context).ti
    ti.xcom_push(
        key=DriftMonitorKeys.DRIFT_SUMMARY,
        value=has_drift_xcom.drift_summary
    )

    if has_drift_xcom.drift_detected:
        return check_current_model_deployment_workflow.__name__
    else:
        return no_action.__name__