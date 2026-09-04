import threading
import time

import pytest

from services.shared.src.services.idempotency import AlreadyProcessed, IdempotencyGuard, IdempotencyStore

def test_already_processed_is_exception():
    assert issubclass(AlreadyProcessed, Exception)

def test_already_processed_can_be_raised():
    with pytest.raises(AlreadyProcessed):
        raise AlreadyProcessed()

import threading
import time
import pytest

@pytest.fixture
def idempotency_store() -> IdempotencyStore:
    return IdempotencyStore(ttl=60, cleanup_interval=9999)

def test_usage(idempotency_store: IdempotencyStore):
    with idempotency_store.guard("k"):
        pass

def test_success_for_distinct_keys(idempotency_store: IdempotencyStore):
    idempotency_store.completed["x"] = time.monotonic() + 60
    with idempotency_store.guard("y"):
        pass

def test_failure_for_duplicate_keys(idempotency_store: IdempotencyStore):
    idempotency_store.completed["k"] = time.monotonic() + 60
    with pytest.raises(AlreadyProcessed):
        with idempotency_store.guard("k"):
            pass

def test_key_removal_after_success(idempotency_store: IdempotencyStore):
    with idempotency_store.guard("k"):
        pass
    assert len(idempotency_store) == 0

def test_key_persistence_after_failure(idempotency_store: IdempotencyStore):
    try:
        with idempotency_store.guard("k"):
            raise RuntimeError
    except RuntimeError:
        pass
    assert "k" in idempotency_store.completed

def test_reprocessing_success_for_expired_key(idempotency_store: IdempotencyStore):
    idempotency_store.completed["k"] = time.monotonic() - 1
    with idempotency_store.guard("k"):
        pass

def test_purge_removal_for_expired_keys(idempotency_store: IdempotencyStore):
    idempotency_store.completed["old"] = time.monotonic() - 1
    idempotency_store.completed["live"] = time.monotonic() + 60

    removed = idempotency_store.purge_expired()

    assert removed == 1
    assert "old" not in idempotency_store.completed
    assert "live" in idempotency_store.completed

def test_items_size(idempotency_store: IdempotencyStore):
    assert len(idempotency_store) == 0

    idempotency_store.completed["a"] = time.monotonic() + 60
    idempotency_store.completed["b"] = time.monotonic() + 60

    assert len(idempotency_store) == 2

def test_cleanup_thread_eventually_purges():
    store = IdempotencyStore(ttl=0.05, cleanup_interval=0.05)

    store.completed["stale"] = time.monotonic() - 1
    time.sleep(1)

    assert "stale" not in store.completed

def test_only_one_key_is_accepted_in_concurrent_setting(idempotency_store: IdempotencyStore):
    concurrent_items = 10
    barrier = threading.Barrier(concurrent_items)

    inside = []
    def attempt():
        barrier.wait()
        try:
            with idempotency_store.guard("shared"):
                inside.append(1)
        except AlreadyProcessed:
            pass

    threads = [threading.Thread(target=attempt) for _ in range(concurrent_items)]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

    assert len(inside) == 1