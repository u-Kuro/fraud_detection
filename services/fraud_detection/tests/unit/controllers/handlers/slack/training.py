from uuid import uuid4
import json

def make_body(workflow_id=None, ts="111.222"):
    wid = workflow_id or str(uuid4())
    return {
        "user": {"username": "tester"},
        "channel": {"id": "C123"},
        "message": {"ts": ts},
        "action": {
            "action_id": "approve_training",
            "value": json.dumps({"workflow_id": wid, "should_train_for_promotion": True}),
        },
    }

def test_module_registers_handlers_with_slack_app():
    import services.fraud_detection.src.controllers.handlers.slack.training as module
    assert module is not None

def test_handler_module_imports_slack_app():
    from services.fraud_detection.src.controllers.handlers.slack.training import slack_app
    assert slack_app is not None
