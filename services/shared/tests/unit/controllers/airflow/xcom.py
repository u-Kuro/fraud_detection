import json

from mock_open import MockOpen
from pytest_mock import MockerFixture

from services.shared.src.controllers.airflow.xcom import xcom_push

def test_xcom_push(mocker: MockerFixture):
    mocker.patch("os.makedirs")
    opener = MockOpen()
    mocker.patch("builtins.open", opener)

    data = {"key": "value", "number": 42}
    xcom_push(data)

    with open("/airflow/xcom/return.json") as file:
        assert json.loads(file.read()) == json.loads(json.dumps(data))