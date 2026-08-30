from dataclasses import dataclass

@dataclass(frozen=True)
class AirflowConfig:
    environment_prefix: str = "AIRFLOW_VAR_"