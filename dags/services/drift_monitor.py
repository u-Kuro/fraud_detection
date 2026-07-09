from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sdk import Variable, task
from kubernetes import client as k8s

from dags.modules.configs.airflow.drift_monitor import drift_monitor_keys_config
from dags.modules.schemas.airflow import AirflowTaskContext
from dags.modules.schemas.airflow.drift_monitor import HasDriftXCom
from dags.repositories.postgres.model_deployment_workflows import check_current_model_deployment_workflow
from dags.services.airflow_operators import no_action

check_for_drift_task_id = "check_for_drift"
check_for_drift = KubernetesPodOperator(
    task_id=check_for_drift_task_id,
    name="drift-monitor",
    namespace="default",
    image=f"{Variable.get("ecr_registry")}/drift-monitor:latest",
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
        key=drift_monitor_keys_config.DRIFT_SUMMARY_KEY,
        value=has_drift_xcom.drift_summary
    )

    if has_drift_xcom.drift_detected:
        return check_current_model_deployment_workflow.__name__
    else:
        return no_action.__name__