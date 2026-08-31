from airflow.sdk import dag

from dags.model_lifecycle_orchestrator.on_training_decision.controllers.slack import initialize_promotion_approval, update_promotion_approval
from dags.model_lifecycle_orchestrator.on_training_decision.repositories.postgres.model_deployment_workflows import update_approved_training_workflow, delete_rejected_training_workflow, update_trained_model_info_in_workflow, update_promotion_pending_workflow
from dags.model_lifecycle_orchestrator.on_training_decision.services.tasks import get_training_decision, train_model, check_training_decision
from dags.shared.modules.configs.project import ProjectConfig
from dags.shared.modules.utilities.airflow.airflow import sequence
from dags.shared.services.slack import slack_failure_alert

@dag(
    max_active_runs=1,
    default_args={
        "on_failure_callback": slack_failure_alert
    },
    is_paused_upon_creation=False,
    tags=[ProjectConfig.project_name, "triggered", "training", "decision"]
)
def on_training_decision():
    sequence(
        training_decision := get_training_decision(),
        check_training_decision(training_decision),
        [
            sequence(
                update_approved_training_workflow(training_decision),
                train_model_result := train_model(),
                update_trained_model_info_in_workflow(
                    training_decision=training_decision,
                    train_model_result=train_model_result,
                ),
                model_deployment_workflow_for_promotion := initialize_promotion_approval(train_model_result),
                update_promotion_pending_workflow(
                    training_decision=training_decision,
                    model_deployment_workflow_for_promotion=model_deployment_workflow_for_promotion,
                ),
                update_promotion_approval(
                    training_decision=training_decision,
                    train_model_result=train_model_result,
                    model_deployment_workflow_for_promotion=model_deployment_workflow_for_promotion,
                )
            ),

            delete_rejected_training_workflow(training_decision)
        ]
    )

on_training_decision()