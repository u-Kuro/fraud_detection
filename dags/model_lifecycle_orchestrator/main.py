from datetime import datetime, timedelta

from airflow.providers.standard.operators import branch
from airflow.sdk import dag

from dags.model_lifecycle_orchestrator.modules.schemas.airflow.xcom import DispatchTrainingApprovalBranches
from dags.model_lifecycle_orchestrator.repositories.postgres.model_deployments import has_any_active_model
from dags.model_lifecycle_orchestrator.services.tasks import invalidate_expired_challenger_model, drift_check, \
    dispatch_training_approval, has_drift

from dags.shared.modules.configs.airflow.airflow import DagIDs, AirflowConfig
from dags.shared.services.airflow_operators import no_action


@dag(
    dag_id=DagIDs.model_lifecycle_orchestrator,
    schedule="0 */6 * * *",
    start_date=datetime(2026, 1, 1),
    max_active_runs=1,
    catchup=True,
    default_args={
        "owner": AirflowConfig.owner,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": False
    },
    tags=["mle", "model", "lifecycle", "monitor"]
)
def model_lifecycle_monitor():
    """

    trigger dag (check and replace expired challenger model)
    if has model
        check drift
            if drifted
                steps()
            else
                no_action
    has no model
        steps()

    def steps()
        has no workflow
            post train pending workflow (cold-start)
        has 1 workflow
            is workflow train_pending
                replace workflow (cold-start)
            is workflow promotion_pending
                post train pending workflow (cold-start model replacement)
            is workflow train_pending_replacement
                assert should not happen
        has 2 workflow DESC
            is workflow[1] not promote_pending
                assert should not happen
            is workflow[0] train_pending
                replace workflow (cold-start model replacement)
            is workflow[0] train_pending_replacement
                no_action
            is workflow promotion_pending
                assert should not happen
    """

    # TODO - 19/07/2026 Continue here main (first-off dispatch_training_approval task_group is unfinished)
    invalidate_expired_challenger_model() \
    >> has_any_active_model() >> [
        drift_check \
        >> has_drift() >> [
            dispatch_training_approval(branch=DispatchTrainingApprovalBranches.drifted),
            no_action()
        ],
        dispatch_training_approval(branch=DispatchTrainingApprovalBranches.cold_start)
    ]

    # BELOW is dispatch_training_approval
    # we can only add task in task groups inside groups (already set during construction time)
    # still we can probably reuse non task functions for reusable duplicated actions
    # it may be better this way too since we will be forced to actually name task inside groups with same task id
    # and force us to categorize tasks and naming

    # I think its better to have DAG on specific pipeline logic (reduction will happen on task_group and helps better dag structure readability)
    # Only separate when they actually are and should be separate.
    # e.g. challenger model rotation can be scheduled too so keeping it separate can be helpful?
    """
    def steps(is-cold-start xcom to show slack approval properly)
        has no workflow
            post train pending workflow (cold-start or retraining)
        has 1 workflow
            is workflow train_pending
                replace workflow (cold-start or retraining)
            is workflow promotion_pending
                post train pending workflow (cold-start or retraining model replacement)
            is workflow train_pending_replacement
                assert should not happen
        has 2 workflow DESC
            is workflow[1] not promote_pending
                assert should not happen
            is workflow[0] train_pending
                replace workflow (cold-start or retraining model replacement)
            is workflow[0] train_pending_replacement
                no_action
            is workflow promotion_pending
                assert should not happen
    """
    # check_current_model_deployment_workflow() >> [
    #     # probably should just use xcom to do training or replacement (along with cold-start or retraining).
    #     # so to keep same task names to avoid too much duplicate
    #
    #     # post train pending workflow (cold-start or retraining depends on trigger for slack post)
    #     initialize_train_pending_workflow()  # add item first to avoid not finding it when slack approval is posted
    #     >> initialize_training_approval()  # post slack approval without action to avoid inconsistency
    #     >> update_train_pending_workflow()  # update item with posted slack ts
    #     >> update_training_approval(),  # update slack with the action buttons
    #
    #     # replace workflow (cold-start or retraining)
    #     invalidate_old_training_approval()  # invalidating (greying out. not delete) training approval to avoid breakage
    #     >> reinitialize_train_pending_workflow()  # setting new workflow (e.g. date)
    #     >> initialize_training_approval()  # post slack approval without action to avoid inconsistency
    #     >> update_train_pending_workflow()  # update item with posted slack ts
    #     >> update_training_approval(),  # update slack with the action buttons
    #
    #     # post train pending workflow (cold-start or retraining model replacement depends on trigger for slack post)
    #     initialize_train_pending_workflow()  # add item first to avoid not finding it when slack approval is posted
    #     >> initialize_training_approval()  # post slack approval without action to avoid inconsistency
    #     >> update_train_pending_workflow()  # update item with posted slack ts
    #     >> update_training_approval(),  # update slack with the action buttons
    #
    #     # replace workflow (cold-start or retraining model replacement)
    #     invalidate_old_training_approval()  # invalidating (greying out. not delete) training approval to avoid breakage
    #     >> reinitialize_train_pending_workflow()  # setting new workflow (e.g. date)
    #     >> initialize_training_approval()  # post slack approval without action to avoid inconsistency
    #     >> update_train_pending_workflow()  # update item with posted slack ts
    #     >> update_training_approval(),  # update slack with the action buttons
    #
    #     no_action()
    # ]

    # has_any_active_model() >> [
    #     has_expired_promote_pending_workflow_with_replacement() >> [
    #         replace_expired_model()
    #         >> delete_expired_model()
    #         >> delete_expired_mlflow_run(),
    #         no_action()
    #     ]
    #     >> drift_check
    #     >> has_drift() >> [
    #         check_current_model_deployment_workflow() >> [
    #             post_retraining_approval()
    #             >> create_train_pending_workflow(),
    #             update_retraining_approval()
    #             >> update_training_pending_workflow(),
    #             no_action()
    #         ],
    #         no_action()
    #     ],
    #     has_no_ongoing_model_deployment_workflow() >> [
    #         post_cold_start_training_approval()
    #         >> create_train_pending_workflow(),
    #         no_action()
    #     ]
    # ]

model_lifecycle_monitor()