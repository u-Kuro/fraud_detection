"""
drift_monitor DAG — runs every 6 hours.

Container handles all Slack posting and DB state. XCom result:
  {"action": "wait_approval"}  → sensor polls training_approved, then triggers training
  {"action": "exit"}           → nothing further to do this tick
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from kubernetes import client as k8s

KUBECONFIG = "/usr/local/airflow/dags/kubeconfig.yaml"
ECR_REGISTRY = Variable.get("ecr_registry", default_var="000000000000.dkr.ecr.us-east-1.amazonaws.com")

DEFAULT_ARGS = {
    "owner":            "mle",
    "retries":          1,
    "retry_delay":      timedelta(minutes=5),
    "email_on_failure": False,
}

_SECRET = [k8s.V1EnvFromSource(secret_ref=k8s.V1SecretEnvSource(name="mle-pipeline-secret"))]
_PULL   = [k8s.V1LocalObjectReference(name="ecr-secret")]


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
        image=f"{ECR_REGISTRY}/fraud-detection-drift-monitor:latest",
        image_pull_policy="Always",
        image_pull_secrets=_PULL,
        env_from=_SECRET,
        do_xcom_push=True,
        get_logs=True,
        is_delete_operator_pod=True,
        startup_timeout_seconds=120,
        config_file=KUBECONFIG,
    )

    @task.branch(task_id="route_after_drift_check")
    def route_after_drift_check(ti=None):
        raw    = ti.xcom_pull(task_ids="run_drift_check")
        result = json.loads(raw) if isinstance(raw, str) else (raw or {})
        return "wait_for_approval" if result.get("action") == "wait_approval" else "no_action"

    @task.sensor(
        task_id="wait_for_approval",
        poke_interval=60,          # poll every minute
        timeout=604800,            # 1-week timeout (DAG will fail if no approval in a week)
        mode="reschedule",         # releases the worker slot between pokes
    )
    def wait_for_approval():
        hook = PostgresHook(postgres_conn_id="fraud_detection_postgres")
        row  = hook.get_first(
            "SELECT training_approved::INTEGER FROM pipeline_state WHERE state = 'drift_pending' LIMIT 1"
        )
        return row is not None and bool(row[0])

    trigger = TriggerDagRunOperator(
        task_id="trigger_training_pipeline",
        trigger_dag_id="training_pipeline",
        wait_for_completion=False,
    )

    no_action = EmptyOperator(task_id="no_action")

    branch = route_after_drift_check()
    run_drift_check >> branch >> [wait_for_approval() >> trigger, no_action]


drift_monitor_dag()