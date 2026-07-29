from dataclasses import dataclass

@dataclass(frozen=True)
class PostgresTableKeys:
    projects: str = "projects"
    model_deployment_workflows: str = "model_deployment_workflows"
    model_deployments: str = "model_deployments"
    transaction_inferences: str = "transaction_inferences"