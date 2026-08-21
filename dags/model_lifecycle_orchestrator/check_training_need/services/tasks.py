from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import task_group, task, get_current_context
from kubernetes.client import models

from dags.model_lifecycle_orchestrator.check_training_need.controllers.slack import initialize_training_approval, update_training_approval, invalidate_old_training_approval, invalidate_expired_promotion_approval
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.branches import NoActionBranches, SetupTrainingApprovalBranches, DispatchTrainingApprovalBranches
from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.xcom import HasDriftXCom
from dags.model_lifecycle_orchestrator.check_training_need.repositories.mlflow.registered_model import replace_expired_model, delete_expired_model
from dags.model_lifecycle_orchestrator.check_training_need.repositories.mlflow.run import delete_expired_mlflow_run
from dags.model_lifecycle_orchestrator.check_training_need.repositories.postgres.model_deployment_workflows import has_expired_promote_pending_workflow_with_replacement, delete_expired_promote_pending_workflow, update_train_pending_workflow, check_current_model_deployment_workflows, initialize_train_pending_workflow, reinitialize_train_pending_workflow
from dags.shared.modules.configs.airflow.airflow import AirflowConfig
from dags.shared.modules.configs.ecr import ECRConfig, ECRImageKeys, ECRSecretKeys
from dags.shared.modules.configs.kubernetes import K8sConfig, K8sConfigMapKeys, K8sSecretKeys
from dags.shared.modules.utilities.airflow.xcom import build_task_id

def no_action(branch: NoActionBranches) -> EmptyOperator:
    return EmptyOperator(task_id=build_task_id((no_action.__name__, branch)))

@task_group(group_id="invalidate_expired_challenger_model")
def invalidate_expired_challenger_model() -> None:
    has_expired_promote_pending_workflow_with_replacement() >> [
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
    @task_group(group_id=build_task_id((dispatch_training_approval.__name__, branch)))
    def group() -> None:
        check_current_model_deployment_workflows(branch=branch) >> [
            initialize_train_pending_workflow() \
            >> setup_training_approval(branch=SetupTrainingApprovalBranches.post),

            invalidate_old_training_approval() \
            >> reinitialize_train_pending_workflow() \
            >> setup_training_approval(branch=SetupTrainingApprovalBranches.replace),

            no_action()
        ]

    return group()

def drift_check() -> KubernetesPodOperator:
     return KubernetesPodOperator(
        task_id=drift_check.__name__,
        name=drift_check.__name__,
        namespace=K8sConfig.namespace,
        config_file=AirflowConfig.kubeconfig_file_path,
        image=f"{ECRConfig.ECR_URL}/{ECRImageKeys.drift_check}:latest",
        image_pull_policy="Always",
        image_pull_secrets=[
            models.V1LocalObjectReference(
                name=ECRSecretKeys.ecr_secret
            )
        ],
        env_from=[
            models.V1EnvFromSource(
                config_map_ref=models.V1ConfigMapEnvSource(
                    name=K8sConfigMapKeys.platform_infrastructure
                )
            ),
            models.V1EnvFromSource(
                secret_ref=models.V1SecretEnvSource(
                    name=K8sSecretKeys.mle_pipeline_secret
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
            DispatchTrainingApprovalBranches.drifted,
            check_current_model_deployment_workflows.__name__
        ))
    else:
        return build_task_id((
            no_action.__name__,
            NoActionBranches.no_drift
        ))