from dataclasses import dataclass

@dataclass(frozen=True)
class PostgresTableKeys:
    projects = "projects"
    model_deployment_workflows = "model_deployment_workflows"
    model_deployments = "model_deployments"