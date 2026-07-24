from dataclasses import dataclass

@dataclass(frozen=True)
class ModelDeploymentsColumnKeys:
    id = "id"
    created_at = "created_at"
    project_id = "project_id"
    name = "name"
    version = "version"
    dataset_min_timestamp = "dataset_min_timestamp"
    dataset_max_timestamp = "dataset_max_timestamp"
    active = "active"