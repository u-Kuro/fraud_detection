from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.sdk import task_group, task
from airflow.sdk.definitions._internal.node import DAGNode
from kubernetes import client as k8s

from dags.model_lifecycle_orchestrator.controllers.slack import invalidate_old_training_approval, \
    initialize_training_approval, update_training_approval
from dags.model_lifecycle_orchestrator.modules.schemas.airflow.branches import DispatchTrainingApprovalBranches, \
    SetupTrainingApprovalBranches
from dags.model_lifecycle_orchestrator.modules.schemas.airflow.xcom import HasDriftXCom
from dags.model_lifecycle_orchestrator.repositories.mlflow.registered_model import replace_expired_model, delete_expired_model
from dags.model_lifecycle_orchestrator.repositories.mlflow.run import delete_expired_mlflow_run
from dags.model_lifecycle_orchestrator.repositories.postgres.model_deployment_workflows import \
    has_expired_promote_pending_workflow_with_replacement, delete_expired_promote_pending_workflow, \
    check_current_model_deployment_workflows, initialize_train_pending_workflow, reinitialize_train_pending_workflow, \
    update_train_pending_workflow
from dags.shared.modules.configs.ecr import ECRConfig
from dags.shared.services.airflow_operators import no_action

@task_group(
    group_id="invalidate_expired_challenger_model",
    prefix_group_id=False
)
def invalidate_expired_challenger_model() -> None:
    has_expired_promote_pending_workflow_with_replacement() >> [
        replace_expired_model()
        >> delete_expired_model()
        >> delete_expired_mlflow_run()
        >> delete_expired_promote_pending_workflow(),
        no_action()
    ]

def setup_training_approval(branch: SetupTrainingApprovalBranches) -> DAGNode:
    @task_group(group_id=f"{setup_training_approval.__name__}.{branch}")
    def group() -> None:
        initialize_training_approval() \ # post slack approval without action to avoid inconsistency
        >> update_train_pending_workflow() \  # update item with posted slack ts
        >> update_training_approval() # update slack with the action buttons

    return group()

def dispatch_training_approval(branch: DispatchTrainingApprovalBranches) -> DAGNode:
    # TODO - 21/07/2026 Need to check each nested tasks included here
    @task_group(group_id=f"{dispatch_training_approval.__name__}.{branch}")
    def group() -> None:
        check_current_model_deployment_workflows(branch=branch) >> [
            # probably should just use xcom to do training or replacement (along with cold-start or retraining).
            # so to keep same task names to avoid too much duplicate

            # post train pending workflow (cold-start or retraining depends on trigger for slack post)
            initialize_train_pending_workflow() # add item first to avoid not finding it when slack approval is posted
            >> setup_training_approval(branch=SetupTrainingApprovalBranches.post),

            # replace workflow (cold-start or retraining)
            invalidate_old_training_approval() # invalidating (greying out. not delete) training approval to avoid breakage
            >> reinitialize_train_pending_workflow() # setting new workflow (e.g. date)
            >> setup_training_approval(branch=SetupTrainingApprovalBranches.replace),

            no_action()
        ]

    return group()

drift_check_task_id = "drift_check"
drift_check = KubernetesPodOperator(
    task_id=drift_check_task_id,
    name=drift_check_task_id,
    namespace="default",
    image=f"{ECRConfig.ECR_URL}/drift-check:latest",
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
    do_xcom_push=True,
    startup_timeout_seconds=120,
    config_file="/usr/local/airflow/dags/kubeconfig.yaml",
)

@task.branch(task_id="has_drift")
def has_drift(**context):
    has_drift_xcom = HasDriftXCom.from_context(context)

    if has_drift_xcom.drift_detected:
        return ".".join((
            dispatch_training_approval.__name__,
            DispatchTrainingApprovalBranches.drifted,
            check_current_model_deployment_workflows.__name__
        ))
    else:
        return no_action.__name__

# trigger_training_approval_dispatch_task_id = "trigger_training_approval_dispatch"
# trigger_training_approval_dispatch = TriggerDagRunOperator(
#     task_id=trigger_training_approval_dispatch_task_id,
#     trigger_dag_id=DagIDs.TRAINING_APPROVAL_DISPATCH,
#     wait_for_completion=True
# )