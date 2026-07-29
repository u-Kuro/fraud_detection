from services.shared.services.idempotency import IdempotencyStore

slack_action_store = IdempotencyStore(ttl=10.0)