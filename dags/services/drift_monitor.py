from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sdk import Variable
from kubernetes import client as k8s

run_drift_monitor = KubernetesPodOperator(
    task_id="run_drift_monitor",
    name="drift-monitor-{{ ds_nodash }}",
    namespace="default",
    image=f"{Variable.get("ecr_registry")}/fraud-detection-drift-monitor:latest",
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
    startup_timeout_seconds=120,
    config_file="/usr/local/airflow/dags/kubeconfig.yaml",
)