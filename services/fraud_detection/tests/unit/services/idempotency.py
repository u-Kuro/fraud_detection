from services.fraud_detection.src.services.idempotency import slack_action_store
from services.shared.src.services.idempotency import IdempotencyStore

def test_slack_action_store_is_idempotency_store():
    assert isinstance(slack_action_store, IdempotencyStore)

def test_slack_action_store_ttl():
    assert slack_action_store.ttl == 10.0
