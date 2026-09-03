from unittest.mock import MagicMock

from services.fraud_detection.src.services.slack import common_callback_configurations, update_message

def test_update_message_calls_chat_update(mocker):
    mock_client = MagicMock()
    body = {"channel": {"id": "C123"}, "message": {"ts": "111.222"}}
    update_message(client=mock_client, body=body, text_markdown="hello *world*")
    mock_client.chat_update.assert_called_once()

def test_update_message_uses_channel_id(mocker):
    mock_client = MagicMock()
    body = {"channel": {"id": "C999"}, "message": {"ts": "111.000"}}
    update_message(client=mock_client, body=body, text_markdown="test")
    call_kwargs = mock_client.chat_update.call_args[1]
    assert call_kwargs["channel"] == "C999"

def test_update_message_uses_message_ts(mocker):
    mock_client = MagicMock()
    body = {"channel": {"id": "C123"}, "message": {"ts": "999.111"}}
    update_message(client=mock_client, body=body, text_markdown="test")
    call_kwargs = mock_client.chat_update.call_args[1]
    assert call_kwargs["ts"] == "999.111"

def test_update_message_sends_mrkdwn_text(mocker):
    mock_client = MagicMock()
    body = {"channel": {"id": "C1"}, "message": {"ts": "1.0"}}
    update_message(client=mock_client, body=body, text_markdown="*bold text*")
    blocks = mock_client.chat_update.call_args[1]["blocks"]
    assert blocks[0]["text"]["text"] == "*bold text*"
    assert blocks[0]["text"]["type"] == "mrkdwn"

def test_common_callback_configurations_extracts_approved_by():
    body = {"user": {"username": "alice"}, "channel": {"id": "C1"}, "message": {"ts": "1.0"}}
    config = common_callback_configurations(body)
    assert config["approved_by"] == "alice"

def test_common_callback_configurations_extracts_channel_id():
    body = {"user": {"username": "alice"}, "channel": {"id": "C999"}, "message": {"ts": "1.0"}}
    config = common_callback_configurations(body)
    assert config["channel_id"] == "C999"

def test_common_callback_configurations_extracts_message_ts():
    body = {"user": {"username": "alice"}, "channel": {"id": "C1"}, "message": {"ts": "123.456"}}
    config = common_callback_configurations(body)
    assert config["message_ts"] == "123.456"

def test_common_callback_configurations_missing_user_returns_none():
    body = {"channel": {"id": "C1"}, "message": {"ts": "1.0"}}
    config = common_callback_configurations(body)
    assert config["approved_by"] is None

def test_slack_app_is_not_none():
    from services.fraud_detection.src.services.slack import slack_app
    assert slack_app is not None
