import json
from unittest.mock import mock_open

from pytest_mock import MockerFixture

from services.shared.src.controllers.airflow.xcom import xcom_push

def test_xcom_push_data_matches(mocker: MockerFixture):
    opener = mock_open()
    mocker.patch("os.makedirs")
    mocker.patch("builtins.open", opener)

    data = {"key": "value", "number": 42}
    xcom_push(data)

    handle = opener.return_value.__enter__.return_value
    written = "".join(call_list.args[0] for call_list in handle.write.call_args_list)

    assert json.loads(written) == json.loads(json.dumps(data))