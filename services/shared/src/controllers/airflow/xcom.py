import json, os

from services.shared.src.modules.configs.airflow import AirflowConfig

def xcom_push(data: dict):
    os.makedirs(os.path.dirname(AirflowConfig.xcom_file_path), exist_ok=True)
    with open(AirflowConfig.xcom_file_path, "w") as file:
        json.dump(data, file)