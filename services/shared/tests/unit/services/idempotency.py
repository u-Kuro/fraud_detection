import threading
import time

import pytest

from services.shared.src.services.idempotency import IdempotencyStore, AlreadyProcessed

class TestAlreadyProcessed:
    def test_identity(self):
        assert issubclass(AlreadyProcessed, Exception)

    def test_raise(self):
        with pytest.raises(AlreadyProcessed):
            raise AlreadyProcessed()

class TestIdempotencyStore:
    @pytest.fixture
    def idempotency_store(self) -> IdempotencyStore:
        return IdempotencyStore(ttl=60, cleanup_interval=9999)

    def test_usage(self, idempotency_store: IdempotencyStore):
        with idempotency_store.guard("k"):
            pass

    def test_success_for_distinct_keys(self, idempotency_store: IdempotencyStore):
        idempotency_store.completed["x"] = time.monotonic() + 60
        with idempotency_store.guard("y"):
            pass

    def test_failure_for_duplicate_keys(self, idempotency_store: IdempotencyStore):
        idempotency_store.completed["k"] = time.monotonic() + 60
        with pytest.raises(AlreadyProcessed):
            with idempotency_store.guard("k"):
                pass

    def test_key_removal_after_success(self, idempotency_store: IdempotencyStore):
        with idempotency_store.guard("k"):
            pass
        assert len(idempotency_store) == 0

    def test_key_persistence_after_failure(self, idempotency_store: IdempotencyStore):
        try:
            with idempotency_store.guard("k"):
                raise RuntimeError
        except RuntimeError:
            pass
        assert "k" in idempotency_store.completed

    def test_success_for_expired_key_reprocessing(self, idempotency_store: IdempotencyStore):
        idempotency_store.completed["k"] = time.monotonic() - 1
        with idempotency_store.guard("k"):
            pass

    def test_purge_removal_for_expired_keys(self, idempotency_store: IdempotencyStore):
        idempotency_store.completed["old"] = time.monotonic() - 1
        idempotency_store.completed["live"] = time.monotonic() + 60

        removed = idempotency_store.purge_expired()

        assert removed == 1
        assert "old" not in idempotency_store.completed
        assert "live" in idempotency_store.completed

    def test_items_size(self, idempotency_store: IdempotencyStore):
        assert len(idempotency_store) == 0

        idempotency_store.completed["a"] = time.monotonic() + 60
        idempotency_store.completed["b"] = time.monotonic() + 60

        assert len(idempotency_store) == 2

    def test_cleanup(self):
        store = IdempotencyStore(ttl=0.05, cleanup_interval=0.05)

        store.completed["stale"] = time.monotonic() - 1
        time.sleep(1)

        assert "stale" not in store.completed

    def test_only_one_key_is_accepted_in_concurrent_setting(self, idempotency_store: IdempotencyStore):
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