# import json, os
#
# def write_xcom(payload: dict) -> None:
#     xcom_dir = "/airflow/xcom"
#     if os.path.isdir(xcom_dir):
#         with open(f"{xcom_dir}/return.json", "w") as f:
#             json.dump(payload, f)