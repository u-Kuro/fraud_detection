import json
from datetime import datetime, timedelta

from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sdk import Variable, dag, task
from kubernetes import client as k8s
from sqlalchemy import create_engine, text

@dag(
    dag_id="drift_monitor", schedule="0 */6 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={
        "owner": "mle",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": False
    },
    tags=["mle", "drift"]
)
def drift_monitor_dag():
    run_drift_check = KubernetesPodOperator(
        task_id="run_drift_check",
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
                secret_ref=k8s.V1SecretEnvSource(
                    name="mle-pipeline-secret"
                )
            ),
        ],
        do_xcom_push=True,
        get_logs=True,
        is_delete_operator_pod=True,
        startup_timeout_seconds=120,
        config_file="/usr/local/airflow/dags/kubeconfig.yaml",
    )

    @task.branch
    def route(ti=None):
        raw = ti.xcom_pull(task_ids="run_drift_check")
        result = json.loads(raw) if isinstance(raw, str) else (raw or {})
        return (
            "wait_for_approval"
            if result.get("action") == "wait_approval"
            else "no_action"
        )

    # TODO - this is not right. there can be multiple state = 'drift_pending' approval from slack should be sent to fraud_detection and that action in fraud_detection should call a dag
    @task.sensor(
        task_id="wait_for_approval",
        poke_interval=60,
        timeout=604800,
        mode="reschedule"
    )
    def wait_for_approval():
        engine = create_engine("postgresql+psycopg2://", pool_pre_ping=True)
        try:
            with engine.connect() as connection:
                return connection.execute(text("""
                    SELECT training_approved
                    FROM pipeline_state
                    WHERE state = 'drift_pending'
                    LIMIT 1
                """)).scalar()
        finally:
            engine.dispose()

    trigger = TriggerDagRunOperator(
        task_id="trigger_training_pipeline",
        trigger_dag_id="training_pipeline",
        wait_for_completion=False
    )
    no_action = EmptyOperator(task_id="no_action")

    # TODO - route() lints - Expected type 'DependencyMixin | Sequence[DependencyMixin]', got 'str' instead
    # TODO - wait_for_approval() lints - Expected type 'DependencyMixin | Sequence[DependencyMixin]', got 'Any | None' instead
    run_drift_check >> route() >> [wait_for_approval() >> trigger, no_action]

drift_monitor_dag()