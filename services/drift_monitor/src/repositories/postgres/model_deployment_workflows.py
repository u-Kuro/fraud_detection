from pyarrow.lib import UUID
from sqlalchemy import text

from services.drift_monitor.src.repositories.postgres import engine
from shared.modules.configs import postgres_config
from shared.modules.schemas import ModelDeploymentWorkflowState, ModelDeploymentWorkflow

def get_current_model_deployment_workflow() -> ModelDeploymentWorkflow | None:
    with engine.connect() as connection:
        row = connection.execute(text(f"""
            SELECT {",".join(ModelDeploymentWorkflow.model_field_keys())}
            FROM model_deployment_workflows
            WHERE project_id = :project_id
            ORDER BY created_at DESC
            LIMIT 1
        """), {
            "project_id": postgres_config.PROJECT_ID
        }).mappings().fetchone()
    return ModelDeploymentWorkflow.model_validate(row, from_attributes=True) if row else None

def create_train_pending_workflow(workflow_id: UUID, training_approval_slack_ts: str | None) -> None:
    with engine.connect() as connection:
        connection.execute(text(f"""
            INSERT INTO model_deployment_workflows (
                id,
                project_id,
                state,
                training_approved,
                training_approval_slack_ts
            )
            VALUES (
               :id, 
               :project_id, 
               :state,
               :training_approved,
               :training_approval_slack_ts
           )
        """),{
            "id": workflow_id,
            "project_id": postgres_config.PROJECT_ID,
            "state": ModelDeploymentWorkflowState.train_pending,
            "training_approved": False,
            "training_approval_slack_ts": training_approval_slack_ts
        })
        connection.commit()

def update_training_approval_slack_ts(training_approval_slack_ts: str | None, current_model_deployment_workflow: ModelDeploymentWorkflow) -> None:
    with engine.connect() as connection:
        connection.execute(text("""
            UPDATE model_deployment_workflows
            SET training_approval_slack_ts = :training_approval_slack_ts
            WHERE id = :id
        """),{
            "id": current_model_deployment_workflow.id,
            "training_approval_slack_ts": training_approval_slack_ts
        })
        connection.commit()