from pydantic_settings import BaseSettings, SettingsConfigDict

from dags.shared.modules.configs.airflow.airflow import AirflowConfig

class K8sEnvironment(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix=AirflowConfig.environment_prefix,
        case_sensitive=True
    )

    K8S_CONNECTION_ID: str
    K8S_NAMESPACE: str
    K8S_BASE_CONFIG_MAP_NAME: str
    K8S_BASE_SECRET_NAME: str
    K8S_DOCKER_REGISTRY_SECRET_NAME: str

k8s_environment = K8sEnvironment()