from uuid import UUID

from pydantic import validate_call
from sqlalchemy import text

from services.train_model.src.modules.schemas import ModelDeploymentWorkflow
from services.train_model.src.repositories.postgres import engine
from services.shared.modules.schemas import ModelDeploymentWorkflowState

def get_deployment_workflow(id: UUID) -> ModelDeploymentWorkflow:
    with engine.connect() as connection:
        model_deployment_workflow = connection.execute(text(f"""
            SELECT {",".join(ModelDeploymentWorkflow.model_field_keys())}
            FROM model_deployment_workflows
            WHERE id = :id
        """), {
            "id": id
        }).mappings().fetchone()

    if model_deployment_workflow is None:
        raise ValueError(f"ModelDeploymentWorkflow with id={id} not found.")

    return ModelDeploymentWorkflow.model_validate(model_deployment_workflow, from_attributes=True)

def update_deployment_workflow(
    id: UUID,
    registered_model_name: str,
    registered_model_version: int,
    model_dataset_min_timestamp: int,
    model_dataset_max_timestamp: int,
) -> None:
    with engine.connect() as connection:
        connection.execute(text("""
            UPDATE model_deployment_workflows
            SET trained_at = NOW(),
                state = :state,
                registered_model_name = :registered_model_name,
                registered_model_version = :registered_model_version,
                model_dataset_min_timestamp = :model_dataset_min_timestamp,
                model_dataset_max_timestamp = :model_dataset_max_timestamp
            WHERE id = :id
        """), {
            "id": id,
            "state": ModelDeploymentWorkflowState.promote_pending,
            "registered_model_name": registered_model_name,
            "registered_model_version": registered_model_version,
            "model_dataset_min_timestamp": model_dataset_min_timestamp,
            "model_dataset_max_timestamp": model_dataset_max_timestamp,
        })
        connection.commit()

@validate_call()
def update_promotion_approval_slack_ts(
    id: UUID,
    promotion_approval_slack_ts: str | None
) -> None:
    with engine.connect() as connection:
        connection.execute(text("""
            UPDATE model_deployment_workflows
            SET promotion_approval_slack_ts = :promotion_approval_slack_ts
            WHERE id = :id
        """),{
            "id": id,
            "promotion_approval_slack_ts": promotion_approval_slack_ts
        })
        connection.commit()
#
# def begin_promoting(
#     model_name: str,
#     model_version: int,
#     dataset_min_date: datetime,
#     dataset_max_date: datetime,
# ) -> None:
#     with engine.connect() as connection:
#         connection.execute(text("""
#             INSERT INTO model_deployments (
#                 model_name,
#                 model_version,
#                 dataset_min_date,
#                 dataset_max_date,
#                 status
#             )
#             VALUES (
#                 :name,
#                 :model_version,
#                 :dataset_min_date,
#                 :dataset_max_date,
#                 'promoting'
#             )
#             ON CONFLICT (model_name, model_version)
#             DO UPDATE SET status = 'promoting'
#         """), {
#             "model_name": model_name,
#             "model_version": model_version,
#             "dataset_min_date": dataset_min_date,
#             "dataset_max_date": dataset_max_date,
#         })
#         connection.execute(text("""
#             UPDATE model_deployment_workflows
#             SET state = 'promoting'
#         """))
#         connection.commit()
#
#
# def finalize_promotion(
#     model_name: str,
#     model_version: int
# ) -> None:
#     with engine.connect() as connection:
#         connection.execute(text("""
#             UPDATE model_deployments
#             SET status = 'active'
#             WHERE   model_name = :model_name
#                 AND model_version = :model_version
#         """), {
#             "model_name": model_name,
#             "model_version": model_version
#         })
#         connection.execute(text("""
#             DELETE FROM model_deployment_workflows
#         """))
#         connection.commit()
