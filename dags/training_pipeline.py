from __future__ import annotations

import os
from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes import client as k8s
from sqlalchemy import create_engine, text

KUBECONFIG = "/usr/local/airflow/dags/kubeconfig.yaml"
ECR_REGISTRY = Variable.get("ecr_registry", default_var="000000000000.dkr.ecr.us-east-1.amazonaws.com")
IMAGE = f"{ECR_REGISTRY}/training_pipeline_ecr:latest"

DEFAULT_ARGS = {
    "owner": "mle",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
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
        timeout=86400,
        mode="reschedule",
    )
    def wait_for_promotion_approval():
        """Polls pipeline_state until a human approves via the fraud_api webhook."""
        pg_url = (
            f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
            f"@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
        )
        eng = create_engine(pg_url, pool_pre_ping=True)
        with eng.connect() as conn:
            row = conn.execute(text(
                "SELECT drift_approved FROM pipeline_state WHERE state = 'train_pending' LIMIT 1"
            )).fetchone()
        eng.dispose()
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