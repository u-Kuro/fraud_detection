from airflow.sdk import dag

from dags.model_lifecycle_orchestrator.on_promotion_decision.repositories.postgres.model_deployment_workflows import update_approved_promotion_workflow, delete_rejected_promotion_workflow
from dags.model_lifecycle_orchestrator.on_promotion_decision.repositories.postgres.model_deployments import promote_model_deployment
from dags.model_lifecycle_orchestrator.on_promotion_decision.services.tasks import check_promotion_decision, get_promotion_decision, apply_model_deployment, archive_transaction_inferences_used_for_deployed_model
from dags.shared.modules.configs.project import ProjectConfig
from dags.shared.modules.utilities.airflow.airflow import sequence
from dags.shared.services.slack import slack_failure_alert

@dag(
    max_active_runs=1,
    default_args={
        "on_failure_callback": slack_failure_alert
    },
    is_paused_upon_creation=False,
    tags=[ProjectConfig.project_name, "triggered", "promotion", "decision"]
)
def on_promotion_decision():
    sequence(
        promotion_decision := get_promotion_decision(),
        check_promotion_decision(promotion_decision),
        [
            sequence(
                update_approved_promotion_workflow(promotion_decision),
                promoted_model_deployment := promote_model_deployment(promotion_decision),
                apply_model_deployment(),
                archive_transaction_inferences_used_for_deployed_model(promoted_model_deployment)
            ),

            delete_rejected_promotion_workflow(promotion_decision)
        ]
    )

on_promotion_decision()