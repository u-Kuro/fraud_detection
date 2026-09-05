from services.fraud_detection.src.services.idempotency import slack_action_store
from services.shared.src.services.idempotency import IdempotencyStore

def test_slack_action_store_instance():
    assert isinstance(slack_action_store, IdempotencyStore)