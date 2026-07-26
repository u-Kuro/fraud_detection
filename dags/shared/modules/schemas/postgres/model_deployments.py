from dataclasses import dataclass

@dataclass(frozen=True)
class ModelDeploymentsColumnKeys:
    id: str = "id"
    created_at: str = "created_at"
    project_id: str = "project_id"
    name: str = "name"
    version: str = "version"
    mlflow_run_id: str = "mlflow_run_id"
    dataset_min_timestamp: str = "dataset_min_timestamp"
    dataset_max_timestamp: str = "dataset_max_timestamp"
    active: str = "active"