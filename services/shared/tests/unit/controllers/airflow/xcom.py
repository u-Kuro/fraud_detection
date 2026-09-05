import json

import pytest
from services.shared.src.controllers.airflow.xcom import xcom_push
from services.shared.src.modules.configs.airflow import AirflowConfig

@pytest.mark.usefixtures("fs")
def test_xcom_push():
    data = {"key": "value"}
    xcom_push(data)

    with open(AirflowConfig.xcom_file_path) as file:
        result = json.loads(file.read())

    assert result == json.loads(json.dumps(data))