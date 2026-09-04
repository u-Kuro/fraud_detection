import json, os

def xcom_push(data: dict):
    os.makedirs("/airflow/xcom", exist_ok=True)
    with open("/airflow/xcom/return.json", "w") as file:
        json.dump(data, file)