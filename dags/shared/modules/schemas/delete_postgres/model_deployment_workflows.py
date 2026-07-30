from dataclasses import dataclass

@dataclass(frozen=True)
class ModelDeploymentWorkflowsColumnKeys:
    id: str = "id"
    created_at: str = "created_at"
    project_id: str = "project_id"
    state: str = "state"
    training_approved: str = "training_approved"
    promotion_approved: str = "promotion_approved"
    model_trained_at: str = "model_trained_at"
    mlflow_run_id: str = "mlflow_run_id"
    registered_model_name: str = "registered_model_name"
    registered_model_version: str = "registered_model_version"
    model_dataset_min_timestamp: str = "model_dataset_min_timestamp"
    model_dataset_max_timestamp: str = "model_dataset_max_timestamp"
    training_approval_slack_ts: str = "training_approval_slack_ts"
    promotion_approval_slack_ts: str = "promotion_approval_slack_ts"

@dataclass(frozen=True)
class ModelDeploymentWorkflowState:
    train_pending: str = "train_pending"
    promote_pending: str = "promote_pending"
    promote_pending_replacement: str = "promote_pending_replacement"