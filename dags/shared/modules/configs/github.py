from dataclasses import dataclass

@dataclass(frozen=True)
class GitHubConfig:
    connection: str = "github_api"
    owner: str = "u-Kuro"
    repository: str = "fraud_detection"
    reference: str = "main"