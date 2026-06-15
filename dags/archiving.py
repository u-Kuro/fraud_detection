from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes import client as k8s

KUBECONFIG = "/usr/local/airflow/dags/kubeconfig.yaml"
ECR_REGISTRY = Variable.get("ecr_registry", default_var="000000000000.dkr.ecr.us-east-1.amazonaws.com")

DEFAULT_ARGS = {
    "owner": "mle",
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
    "email_on_failure": False,
}


@dag(
    dag_id="archiving",
    schedule="0 2 * * 0",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["mle", "archiving"],
)
def archiving_dag():

    KubernetesPodOperator(
        task_id="run_archiving",
        name="archiving-{{ ds_nodash }}",
        namespace="default",
        image=f"{ECR_REGISTRY}/archiving_ecr:latest",
        image_pull_policy="Always",
        image_pull_secrets=[k8s.V1LocalObjectReference(name="ecr-secret")],
        env_from=[k8s.V1EnvFromSource(
            secret_ref=k8s.V1SecretEnvSource(name="mle-pipeline-secret")
        )],
        get_logs=True,
        is_delete_operator_pod=True,
        startup_timeout_seconds=120,
        config_file=KUBECONFIG,
    )


archiving_dag()