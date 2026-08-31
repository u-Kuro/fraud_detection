from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import task_group, task, get_current_context
from kubernetes.client import models

from dags.model_lifecycle_orchestrator.check_training_need.controllers.slack import initialize_training_approval, update_training_approval, invalidate_old_training_approval, invalidate_expired_promotion_approval
from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.task_ids import NoActionTaskIDs, SetupTrainingApprovalTaskIDs, DispatchTrainingApprovalTaskIDs
from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.k8s.environments import DriftCheckEnvironmentKeys
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.tasks import ActiveModelDeployment, ModelDeploymentWorkflowForTraining
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.xcom import DriftCheckResult
from dags.model_lifecycle_orchestrator.check_training_need.repositories.mlflow.registered_model import replace_expired_model, delete_expired_model
from dags.model_lifecycle_orchestrator.check_training_need.repositories.mlflow.run import delete_expired_mlflow_run
from dags.model_lifecycle_orchestrator.check_training_need.repositories.postgres.model_deployment_workflows import has_expired_promote_pending_workflow_with_replacement, delete_expired_promote_pending_workflow, update_train_pending_workflow, check_current_model_deployment_workflows, initialize_train_pending_workflow, reinitialize_train_pending_workflow, get_expired_model_deployment_workflow_with_its_replacement, get_current_model_deployment_workflow_for_training
from dags.shared.modules.environment.ecr import ecr_environment
from dags.shared.modules.environment.k8s import k8s_environment
from dags.shared.modules.schemas.airflow import TaskContext
from dags.shared.modules.utilities.airflow.airflow import sequence

def no_action(task_id: NoActionTaskIDs) -> EmptyOperator:
    return EmptyOperator(task_id=task_id)

@task_group
def invalidate_expired_challenger_model() -> None:
    sequence(
        expired_and_reserved_model_deployment_workflows := get_expired_model_deployment_workflow_with_its_replacement(),
        has_expired_promote_pending_workflow_with_replacement(expired_and_reserved_model_deployment_workflows),
        [
            sequence(
                invalidate_expired_promotion_approval(expired_and_reserved_model_deployment_workflows),
                replace_expired_model(expired_and_reserved_model_deployment_workflows),
                delete_expired_model(expired_and_reserved_model_deployment_workflows),
                delete_expired_mlflow_run(expired_and_reserved_model_deployment_workflows),
                delete_expired_promote_pending_workflow(expired_and_reserved_model_deployment_workflows)
            ),
            no_action(task_id=NoActionTaskIDs.no_expired_promote_pending_workflow_with_replacement)
        ]
    )

def drift_check_operator(active_model_deployment: ActiveModelDeployment) -> KubernetesPodOperator:
    return KubernetesPodOperator(
        task_id=drift_check_operator.__name__,
        name=drift_check_operator.__name__,
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
                name=DriftCheckEnvironmentKeys.ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID,
                value=active_model_deployment.mlflow_run_id
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

@task_group
def drift_check(active_model_deployment: ActiveModelDeployment | None) -> DriftCheckResult:
    assert active_model_deployment is not None

    @task
    def get_drift_result() -> DriftCheckResult:
        context = TaskContext(get_current_context())
        return context.xcom_pull(pydantic_model=DriftCheckResult)

    sequence(
        drift_check_operator(active_model_deployment),
        drift_result := get_drift_result()
    )

    return drift_result

@task.branch
def has_drift(drift_result: DriftCheckResult):
    context = TaskContext(get_current_context())

    if drift_result.drift_detected:
        return context.resolve_task_id(
            task_id=DispatchTrainingApprovalTaskIDs.drifted
        )
    else:
        return context.resolve_task_id(
            task_id=NoActionTaskIDs.no_drift
        )

def dispatch_training_approval(
    task_id: DispatchTrainingApprovalTaskIDs,
    drift_result: DriftCheckResult | None = None,
):
    @task_group(group_id=task_id)
    def group() -> None:
        sequence(
            current_model_deployment_workflow_for_training := get_current_model_deployment_workflow_for_training(),
            check_current_model_deployment_workflows(current_model_deployment_workflow_for_training),
            [
                sequence(
                    new_model_deployment_workflow_for_training := initialize_train_pending_workflow(current_model_deployment_workflow_for_training),
                    setup_training_approval(
                        task_id=SetupTrainingApprovalTaskIDs.post,
                        model_deployment_workflow_for_training=new_model_deployment_workflow_for_training,
                        drift_result=drift_result,
                    )
                ),

                sequence(
                    invalidate_old_training_approval(
                        model_deployment_workflow_for_training=current_model_deployment_workflow_for_training,
                        drift_result=drift_result,
                    ),
                    reinitialize_train_pending_workflow(current_model_deployment_workflow_for_training),
                    setup_training_approval(
                        task_id=SetupTrainingApprovalTaskIDs.replace,
                        model_deployment_workflow_for_training=current_model_deployment_workflow_for_training,
                        drift_result=drift_result,
                    )
                ),

                no_action(task_id=NoActionTaskIDs.no_expired_workflows)
            ]
        )

    return group()

def setup_training_approval(
    task_id: SetupTrainingApprovalTaskIDs,
    model_deployment_workflow_for_training: ModelDeploymentWorkflowForTraining | None,
    drift_result: DriftCheckResult | None,
):
    @task_group(group_id=task_id)
    def group() -> None:
        sequence(
            updated_model_deployment_workflow_for_training := initialize_training_approval(
                model_deployment_workflow_for_training=model_deployment_workflow_for_training,
                drift_result=drift_result,
            ),
            update_train_pending_workflow(updated_model_deployment_workflow_for_training),
            update_training_approval(
                model_deployment_workflow_for_training=updated_model_deployment_workflow_for_training,
                drift_result=drift_result,
            )
        )

    return group()