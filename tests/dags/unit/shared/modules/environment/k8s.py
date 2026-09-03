import pytest
from pydantic import ValidationError
from dags.shared.modules.environment.k8s import K8sEnvironment

def test_k8s_environment_reads_connection_id(monkeypatch):
    monkeypatch.setenv("AIRFLOW_VAR_K8S_CONNECTION_ID", "k8s_conn")
    monkeypatch.setenv("AIRFLOW_VAR_K8S_NAMESPACE", "airflow")
    monkeypatch.setenv("AIRFLOW_VAR_K8S_BASE_CONFIG_MAP_NAME", "cfg")
    monkeypatch.setenv("AIRFLOW_VAR_K8S_BASE_SECRET_NAME", "sec")
    monkeypatch.setenv("AIRFLOW_VAR_K8S_DOCKER_REGISTRY_SECRET_NAME", "reg")
    env = K8sEnvironment()
    assert env.K8S_CONNECTION_ID == "k8s_conn"

def test_k8s_environment_missing_namespace_raises(monkeypatch):
    monkeypatch.setenv("AIRFLOW_VAR_K8S_CONNECTION_ID", "k8s_conn")
    monkeypatch.setenv("AIRFLOW_VAR_K8S_BASE_CONFIG_MAP_NAME", "cfg")
    monkeypatch.setenv("AIRFLOW_VAR_K8S_BASE_SECRET_NAME", "sec")
    monkeypatch.setenv("AIRFLOW_VAR_K8S_DOCKER_REGISTRY_SECRET_NAME", "reg")
    monkeypatch.delenv("AIRFLOW_VAR_K8S_NAMESPACE", raising=False)
    with pytest.raises(ValidationError):
        K8sEnvironment()

def test_k8s_environment_module_level_instance():
    from dags.shared.modules.environment.k8s import k8s_environment
    assert isinstance(k8s_environment, K8sEnvironment)
