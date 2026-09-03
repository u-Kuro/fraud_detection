import threading
import time

import pytest

from services.shared.src.services.idempotency import AlreadyProcessed, IdempotencyGuard, IdempotencyStore

def test_already_processed_is_exception():
    assert issubclass(AlreadyProcessed, Exception)

def test_already_processed_can_be_raised():
    with pytest.raises(AlreadyProcessed):
        raise AlreadyProcessed()

def test_already_processed_message():
    exc = AlreadyProcessed("duplicate")
    assert str(exc) == "duplicate"

def test_idempotency_store_sets_ttl():
    store = IdempotencyStore(ttl=5.0)
    assert store.ttl == 5.0

def test_idempotency_store_default_cleanup_interval_half_ttl():
    store = IdempotencyStore(ttl=8.0)
    assert store.cleanup_interval == 4.0

def test_idempotency_store_default_cleanup_interval_minimum_one():
    store = IdempotencyStore(ttl=0.5)
    assert store.cleanup_interval == 1.0

def test_idempotency_store_custom_cleanup_interval():
    store = IdempotencyStore(ttl=10.0, cleanup_interval=2.0)
    assert store.cleanup_interval == 2.0

def test_idempotency_store_starts_with_empty_completed():
    store = IdempotencyStore(ttl=5.0)
    assert len(store.completed) == 0

def test_idempotency_store_has_lock():
    store = IdempotencyStore(ttl=5.0)
    assert isinstance(store.lock, type(threading.Lock()))

def test_idempotency_store_guard_returns_guard():
    store = IdempotencyStore(ttl=5.0)
    guard = store.guard("part1", "part2")
    assert isinstance(guard, IdempotencyGuard)

def test_idempotency_store_guard_joins_parts_with_colon():
    store = IdempotencyStore(ttl=5.0)
    guard = store.guard("a", "b", "c")
    assert guard.key == "a:b:c"

def test_idempotency_store_len_counts_active_entries():
    store = IdempotencyStore(ttl=60.0)
    store.completed["key1"] = time.monotonic() + 60.0
    store.completed["key2"] = time.monotonic() + 60.0
    assert len(store) == 2

def test_idempotency_store_len_zero_when_empty():
    store = IdempotencyStore(ttl=5.0)
    assert len(store) == 0

def test_purge_expired_removes_stale_keys():
    store = IdempotencyStore(ttl=5.0)
    store.completed["old"] = time.monotonic() - 1.0
    store.completed["fresh"] = time.monotonic() + 60.0
    removed = store.purge_expired()
    assert removed == 1
    assert "old" not in store.completed
    assert "fresh" in store.completed

def test_purge_expired_returns_zero_when_nothing_stale():
    store = IdempotencyStore(ttl=5.0)
    store.completed["fresh"] = time.monotonic() + 60.0
    removed = store.purge_expired()
    assert removed == 0

def test_purge_expired_clears_all_stale():
    store = IdempotencyStore(ttl=5.0)
    store.completed["a"] = time.monotonic() - 2.0
    store.completed["b"] = time.monotonic() - 1.0
    removed = store.purge_expired()
    assert removed == 2
    assert len(store.completed) == 0

def test_idempotency_guard_records_key_on_enter():
    store = IdempotencyStore(ttl=60.0)
    with store.guard("action", "ts1"):
        pass  # success path removes key
    # After clean exit the key is removed
    assert "action:ts1" not in store.completed

def test_idempotency_guard_raises_already_processed_on_duplicate():
    store = IdempotencyStore(ttl=60.0)
    # Manually place a non-expired entry
    store.completed["x:y"] = time.monotonic() + 60.0
    with pytest.raises(AlreadyProcessed):
        with store.guard("x", "y"):
            pass

def test_idempotency_guard_suppresses_already_processed_from_body():
    # AlreadyProcessed raised INSIDE the with-body is suppressed by __exit__
    store = IdempotencyStore(ttl=60.0)
    # Manually seed a different key so __enter__ does NOT raise
    guard = store.guard("unique", "key")
    guard.__enter__()
    # Now raise AlreadyProcessed from the body — __exit__ should suppress it
    result = guard.__exit__(AlreadyProcessed, AlreadyProcessed(), None)
    assert result is True

def test_idempotency_guard_propagates_real_exceptions():
    store = IdempotencyStore(ttl=60.0)
    with pytest.raises(ValueError):
        with store.guard("a", "b"):
            raise ValueError("real error")

def test_idempotency_guard_keeps_key_on_real_exception():
    store = IdempotencyStore(ttl=60.0)
    try:
        with store.guard("a", "b"):
            raise ValueError("boom")
    except ValueError:
        pass
    # Key should still be present because the action did not complete cleanly
    assert "a:b" in store.completed

def test_idempotency_guard_refs_store_and_key():
    store = IdempotencyStore(ttl=5.0)
    guard = IdempotencyGuard(store=store, key="x:y")
    assert guard.store is store
    assert guard.key == "x:y"
