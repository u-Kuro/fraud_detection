import sys

import pytest
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_boto3_module(mocker):
    sys.modules.update({
        # "boto3": MagicMock(),
        # "boto3.client": MagicMock(),
        "boto3.client.head_bucket": MagicMock(),
        "boto3.client.create_bucket": MagicMock(),
    })

    yield sys.modules["boto3"]

    del sys.modules["boto3"]

@pytest.fixture(autouse=True)
def mock_mlflow_module(mocker):
    sys.modules.update({
        # "mlflow": MagicMock(),
    })

    yield sys.modules["mlflow"]

    del sys.modules["mlflow"]

@pytest.fixture(autouse=True)
def mock_slack_bolt_module():
    sys.modules.update({
        "slack_bolt": MagicMock(),
        "slack_bolt.adapter": MagicMock(),
        "slack_bolt.adapter.socket_mode": MagicMock(),
    })

    yield sys.modules["slack_bolt"]

    del sys.modules["slack_bolt"]

@pytest.fixture(autouse=True)
def mock_sqlalchemy_module(mocker):
    sys.modules.update({
        # "sqlalchemy": MagicMock(),
        # "sqlalchemy.orm.sessionmaker": MagicMock(),
    })

    yield sys.modules["sqlalchemy"]

    del sys.modules["sqlalchemy"]


