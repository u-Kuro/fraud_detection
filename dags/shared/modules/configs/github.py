from dataclasses import dataclass

@dataclass(frozen=True)
class GitHubConfig:
    owner: str = "u-Kuro"
    repository: str = "fraud_detection_platform"