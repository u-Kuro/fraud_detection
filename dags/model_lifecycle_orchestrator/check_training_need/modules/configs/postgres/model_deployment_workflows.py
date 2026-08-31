from dataclasses import dataclass
from enum import StrEnum

from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflows

@dataclass(frozen=True)
class ModelDeploymentWorkflowsConfig:
    challenger_model_expiration_days: int = 7

class ReservedModelDeploymentWorkflowLabels(StrEnum):
    registered_model_name = f"reserved_{ModelDeploymentWorkflows.__tablename__}_{ModelDeploymentWorkflows.registered_model_name.key}"
    registered_model_version = f"reserved_{ModelDeploymentWorkflows.__tablename__}_{ModelDeploymentWorkflows.registered_model_version.key}"

class ExpiredModelDeploymentWorkflowsLabels(StrEnum):
    slack_promotion_approval_message_ts = f"expired_{ModelDeploymentWorkflows.__tablename__}_{ModelDeploymentWorkflows.slack_promotion_approval_message_ts.key}"
    id = f"expired_{ModelDeploymentWorkflows.__tablename__}_{ModelDeploymentWorkflows.id.key}"
    mlflow_run_id = f"expired_{ModelDeploymentWorkflows.__tablename__}_{ModelDeploymentWorkflows.mlflow_run_id.key}"
    registered_model_name = f"expired_{ModelDeploymentWorkflows.__tablename__}_{ModelDeploymentWorkflows.registered_model_name.key}"
    registered_model_version = f"expired_{ModelDeploymentWorkflows.__tablename__}_{ModelDeploymentWorkflows.registered_model_version.key}"
