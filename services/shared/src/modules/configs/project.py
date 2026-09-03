from dataclasses import dataclass

@dataclass(frozen=True)
class ProjectConfig:
    project_name: str = "fraud_detection"