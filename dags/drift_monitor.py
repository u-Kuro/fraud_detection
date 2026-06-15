"""
drift_monitor — runs every 6 hours via KubernetesPodOperator.

XCom from the container: {"trigger_training": bool, "reason": str}
Written by the container to /airflow/xcom/return.json.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes import client as k8s

KUBECONFIG = "/usr/local/airflow/dags/kubeconfig.yaml"
ECR_REGISTRY = Variable.get("ecr_registry", default_var="000000000000.dkr.ecr.us-east-1.amazonaws.com")

DEFAULT_ARGS = {
    "owner": "mle",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}


@dag(
    dag_id="drift_monitor",
    schedule="0 */6 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["mle", "drift"],
)
def drift_monitor_dag():

    run_drift_check = KubernetesPodOperator(
        task_id="run_drift_check",
        name="drift-monitor-{{ ds_nodash }}",
        namespace="default",
        image=f"{ECR_REGISTRY}/drift_monitor_ecr:latest",
        image_pull_policy="Always",
        image_pull_secrets=[k8s.V1LocalObjectReference(name="ecr-secret")],
        env_from=[k8s.V1EnvFromSource(
            secret_ref=k8s.V1SecretEnvSource(name="mle-pipeline-secret")
        )],
        do_xcom_push=True,
        get_logs=True,
        is_delete_operator_pod=True,
        startup_timeout_seconds=120,
        config_file=KUBECONFIG,
    )

    @task.branch(task_id="should_trigger_training")
    def should_trigger_training(ti=None):
        raw = ti.xcom_pull(task_ids="run_drift_check")
        result = json.loads(raw) if isinstance(raw, str) else (raw or {})
        return "trigger_training_pipeline" if result.get("trigger_training") else "no_training_needed"

    trigger = TriggerDagRunOperator(
        task_id="trigger_training_pipeline",
        trigger_dag_id="training_pipeline",
        wait_for_completion=False,
    )

    skip = EmptyOperator(task_id="no_training_needed")

    run_drift_check >> should_trigger_training() >> [trigger, skip]


drift_monitor_dag()