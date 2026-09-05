from dataclasses import dataclass

@dataclass(frozen=True)
class AirflowConfig:
    xcom_file_path: str = "/airflow/xcom/return.json"