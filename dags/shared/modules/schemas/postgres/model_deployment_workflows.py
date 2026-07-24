from dataclasses import dataclass

@dataclass(frozen=True)
class ModelDeploymentWorkflowsColumnKeys:
    id = "id"
    created_at = "created_at"
    project_id = "project_id"
    state = "state"
    training_approved = "training_approved"
    promotion_approved = "promotion_approved"
    model_trained_at = "model_trained_at"
    mlflow_run_id = "mlflow_run_id"
    registered_model_name = "registered_model_name"
    registered_model_version = "registered_model_version"
    model_dataset_min_timestamp = "model_dataset_min_timestamp"
    model_dataset_max_timestamp = "model_dataset_max_timestamp"
    training_approval_slack_ts = "training_approval_slack_ts"
    promotion_approval_slack_ts = "promotion_approval_slack_ts"

@dataclass(frozen=True)
class ModelDeploymentWorkflowState:
    train_pending = "train_pending"
    promote_pending = "promote_pending"
    promote_pending_replacement = "promote_pending_replacement"