from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import task_group, task, get_current_context
from kubernetes.client import models

from dags.model_lifecycle_orchestrator.check_training_need.controllers.slack import initialize_training_approval, update_training_approval, invalidate_old_training_approval, invalidate_expired_promotion_approval
from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.data_keys import DriftCheckKeys
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.branches import NoActionBranches, SetupTrainingApprovalBranches, DispatchTrainingApprovalBranches
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.xcom import HasDriftXCom, DriftCheckXCom
from dags.model_lifecycle_orchestrator.check_training_need.repositories.mlflow.registered_model import replace_expired_model, delete_expired_model
from dags.model_lifecycle_orchestrator.check_training_need.repositories.mlflow.run import delete_expired_mlflow_run
from dags.model_lifecycle_orchestrator.check_training_need.repositories.postgres.model_deployment_workflows import has_expired_promote_pending_workflow_with_replacement, delete_expired_promote_pending_workflow, update_train_pending_workflow, check_current_model_deployment_workflows, initialize_train_pending_workflow, reinitialize_train_pending_workflow
from dags.shared.modules.environment.ecr import ecr_environment
from dags.shared.modules.environment.k8s import k8s_environment
from dags.shared.modules.utilities.airflow.xcom import build_task_id

def no_action(branch: NoActionBranches) -> EmptyOperator:
    return EmptyOperator(task_id=build_task_id((no_action.__name__, branch)))

@task_group(group_id="invalidate_expired_challenger_model")
def invalidate_expired_challenger_model() -> None:
    group_id = invalidate_expired_challenger_model.__name__
    has_expired_promote_pending_workflow_with_replacement(group_id=group_id) >> [
        invalidate_expired_promotion_approval() \
        >> replace_expired_model() \
        >> delete_expired_model() \
        >> delete_expired_mlflow_run() \
        >> delete_expired_promote_pending_workflow(),

        no_action(branch=NoActionBranches.no_expired_promote_pending_workflow_with_replacement)
    ]

def setup_training_approval(branch: SetupTrainingApprovalBranches):
    @task_group(group_id=build_task_id((setup_training_approval.__name__, branch)))
    def group() -> None:
        initialize_training_approval() \
        >> update_train_pending_workflow() \
        >> update_training_approval()

    return group()

def dispatch_training_approval(branch: DispatchTrainingApprovalBranches):
    group_id = build_task_id((dispatch_training_approval.__name__, branch))
    @task_group(group_id=group_id)
    def group() -> None:
        check_current_model_deployment_workflows(group_id=group_id) >> [
            initialize_train_pending_workflow() \
            >> setup_training_approval(branch=SetupTrainingApprovalBranches.post),

            invalidate_old_training_approval() \
            >> reinitialize_train_pending_workflow() \
            >> setup_training_approval(branch=SetupTrainingApprovalBranches.replace),

            no_action(branch=NoActionBranches.no_expired_workflows)
        ]

    return group()

def drift_check() -> KubernetesPodOperator:
    context = get_current_context()

    drift_check_xcom = DriftCheckXCom.from_context(context)

    return KubernetesPodOperator(
        task_id=drift_check.__name__,
        name=drift_check.__name__,
        namespace=k8s_environment.K8S_NAMESPACE,
        kubernetes_conn_id=k8s_environment.K8S_CONNECTION_ID,
        image=ecr_environment.DRIFT_CHECK_IMAGE,
        image_pull_policy="Always",
        image_pull_secrets=[
            models.V1LocalObjectReference(
                name=k8s_environment.K8S_DOCKER_REGISTRY_SECRET_NAME
            )
        ],
        env=[
            models.V1EnvVar(
                name=DriftCheckKeys.ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID,
                value=drift_check_xcom.active_model_deployment_mlflow_run_id
            )
        ],
        env_from=[
            models.V1EnvFromSource(
                config_map_ref=models.V1ConfigMapEnvSource(
                    name=k8s_environment.K8S_BASE_CONFIG_MAP_NAME
                )
            ),
            models.V1EnvFromSource(
                secret_ref=models.V1SecretEnvSource(
                    name=k8s_environment.K8S_BASE_SECRET_NAME
                )
            ),
        ],
        do_xcom_push=True,
        startup_timeout_seconds=300,
        get_logs=True,
        log_events_on_failure=True,
        on_finish_action="delete_pod",
    )

@task.branch(task_id="has_drift")
def has_drift():
    context = get_current_context()

    has_drift_xcom = HasDriftXCom.from_context(context)

    if has_drift_xcom.drift_detected:
        return build_task_id((
            dispatch_training_approval.__name__,
            DispatchTrainingApprovalBranches.drifted
        ))
    else:
        return build_task_id((
            no_action.__name__,
            NoActionBranches.no_drift
        ))