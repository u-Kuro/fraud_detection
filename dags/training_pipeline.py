"""
training_pipeline DAG — triggered by drift_monitor when training is approved.

1. run_training        — trains the model; container posts/updates the promotion Slack message.
2. wait_for_promotion  — sensor polls promote_approved in pipeline_state.
3. run_promotion       — promotes candidate to production; calls fraud_detection /internal/reload-model.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from kubernetes import client as k8s

KUBECONFIG    = "/usr/local/airflow/dags/kubeconfig.yaml"
ECR_REGISTRY  = Variable.get("ecr_registry", default_var="000000000000.dkr.ecr.us-east-1.amazonaws.com")
IMAGE         = f"{ECR_REGISTRY}/fraud-detection-training-pipeline:latest"

DEFAULT_ARGS = {
    "owner":            "mle",
    "retries":          1,
    "retry_delay":      timedelta(minutes=10),
    "email_on_failure": False,
}

_SECRET = [k8s.V1EnvFromSource(secret_ref=k8s.V1SecretEnvSource(name="mle-pipeline-secret"))]
_PULL   = [k8s.V1LocalObjectReference(name="ecr-secret")]


@dag(
    dag_id="training_pipeline",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["mle", "training"],
)
def training_pipeline_dag():

    run_training = KubernetesPodOperator(
        task_id="run_training",
        name="training-{{ run_id | slugify }}",
        namespace="default",
        image=IMAGE,
        image_pull_policy="Always",
        image_pull_secrets=_PULL,
        env_from=_SECRET,
        do_xcom_push=True,
        get_logs=True,
        is_delete_operator_pod=True,
        startup_timeout_seconds=300,
        config_file=KUBECONFIG,
    )

    @task.sensor(
        task_id="wait_for_promotion_approval",
        poke_interval=60,
        timeout=604800,    # 1-week timeout
        mode="reschedule",
    )
    def wait_for_promotion_approval():
        """Polls until a human approves via Slack → fraud_detection action handler."""
        hook = PostgresHook(postgres_conn_id="fraud_detection_postgres")
        row  = hook.get_first(
            "SELECT promote_approved::INTEGER FROM pipeline_state WHERE state = 'train_pending' LIMIT 1"
        )
        return row is not None and bool(row[0])

    run_promotion = KubernetesPodOperator(
        task_id="run_promotion",
        name="promotion-{{ run_id | slugify }}",
        namespace="default",
        image=IMAGE,
        image_pull_policy="Always",
        image_pull_secrets=_PULL,
        env_from=_SECRET,
        env_vars=[k8s.V1EnvVar(name="PIPELINE_ACTION", value="promote")],
        get_logs=True,
        is_delete_operator_pod=True,
        startup_timeout_seconds=180,
        config_file=KUBECONFIG,
    )

    run_training >> wait_for_promotion_approval() >> run_promotion


training_pipeline_dag()