from uuid import UUID

from sqlalchemy import text

from dags.repositories.postgres.postgres import engine

def training_approved(workflow_id: UUID):
    with engine.begin() as connection:
        connection.execute(text("""
            UPDATE model_deployment_workflows
            SET training_approved = :training_approved
            WHERE id = :id
        """), {
            "id": workflow_id,
            "training_approved": True
        })

def training_rejected(workflow_id: UUID):
    with engine.begin() as connection:
        connection.execute(text("""
            DELETE FROM model_deployment_workflows
            WHERE id = :id
        """), {
            "id": workflow_id
        })