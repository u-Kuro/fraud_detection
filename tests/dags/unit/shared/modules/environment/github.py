import pytest
from pydantic import ValidationError
from dags.shared.modules.environment.github import GitHubEnvironment

def test_github_environment_reads_connection_id(monkeypatch):
    monkeypatch.setenv("AIRFLOW_VAR_GITHUB_CONNECTION_ID", "github_conn")
    env = GitHubEnvironment()
    assert env.GITHUB_CONNECTION_ID == "github_conn"

def test_github_environment_missing_connection_id_raises(monkeypatch):
    monkeypatch.delenv("AIRFLOW_VAR_GITHUB_CONNECTION_ID", raising=False)
    with pytest.raises(ValidationError):
        GitHubEnvironment()

def test_github_environment_module_level_instance():
    from dags.shared.modules.environment.github import github_environment
    assert isinstance(github_environment, GitHubEnvironment)
