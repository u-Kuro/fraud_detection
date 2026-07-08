from datetime import datetime, timedelta

from airflow.sdk import dag

from dags.modules.configs.dags import dags_config
from dags.services.training_pipeline import run_training


@dag(
    dag_id="training_pipeline",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    max_active_runs=1,
    catchup=True,
    default_args={
        "owner": dags_config.OWNER,
        "retries": 1,
        "retry_delay": timedelta(minutes=10),
        "email_on_failure": False
    },
    tags=["mle", "training"]
)
def training_pipeline_dag():

    run_training()

    # @task.sensor(
    #     task_id="wait_for_promotion_approval",
    #     poke_interval=60,
    #     timeout=604800,
    #     mode="reschedule"
    # )
    # def wait_for_promotion_approval():
    #     from sqlalchemy import create_engine, text
    #
    #     engine = create_engine("postgresql+psycopg2://", pool_pre_ping=True)
    #     try:
    #         with engine.connect() as conn:
    #             return conn.execute(text("""
    #                 SELECT promote_approved
    #                 FROM model_deployment_workflows
    #                 WHERE state = :state
    #                 LIMIT 1
    #             """), {
    #                 "state": ModelDeploymentWorkflowState.train_pending
    #             }).scalar()
    #     finally:
    #         engine.dispose()
    #
    # run_promotion = KubernetesPodOperator(
    #     task_id="run_promotion",
    #     name="promotion-{{ run_id | slugify }}",
    #     namespace="default",
    #     image=f"{Variable.get("ecr_registry")}/training-pipeline:latest",
    #     image_pull_policy="Always",
    #     image_pull_secrets=[
    #         k8s.V1LocalObjectReference(
    #             name="ecr-secret"
    #         )
    #     ],
    #     env_from=[
    #         k8s.V1EnvFromSource(
    #             config_map_ref=k8s.V1ConfigMapEnvSource(
    #                 name="platform-infrastructure"
    #             )
    #         ),
    #         k8s.V1EnvFromSource(
    #             secret_ref=k8s.V1SecretEnvSource(
    #                 name="mle-pipeline-secret"
    #             )
    #         ),
    #     ],
    #     env_vars=[
    #         k8s.V1EnvVar(
    #             name="PIPELINE_ACTION",
    #             value="promote"
    #         )
    #     ],
    #     get_logs=True,
    #     is_delete_operator_pod=True,
    #     startup_timeout_seconds=180,
    #     config_file="/usr/local/airflow/dags/kubeconfig.yaml",
    # )
    #
    # # Rolling restart of fraud_api after promotion so new pods load the new MLflow alias.
    # # bitnami/kubectl image provides kubectl; KUBECONFIG has full cluster access.
    # restart_fraud_api = KubernetesPodOperator(
    #     task_id="restart_fraud_api",
    #     name="restart-fraud-detection-{{ run_id | slugify }}",
    #     namespace="default",
    #     image="bitnami/kubectl:latest",
    #     cmds=[
    #         "kubectl",
    #         "rollout",
    #         "restart",
    #         "deployment/fraud-detection",
    #         "--namespace",
    #         "default"
    #     ],
    #     get_logs=True,
    #     is_delete_operator_pod=True,
    #     startup_timeout_seconds=60,
    #     config_file="/usr/local/airflow/dags/kubeconfig.yaml",
    # )
    #
    # run_training() >> wait_for_promotion_approval() >> run_promotion >> restart_fraud_api


training_pipeline_dag()