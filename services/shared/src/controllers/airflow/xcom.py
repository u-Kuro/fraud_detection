import json, os

os.makedirs("/airflow/xcom", exist_ok=True)

def xcom_push(data: dict):
    with open("/airflow/xcom/return.json", "w") as file:
        json.dump(data, file)