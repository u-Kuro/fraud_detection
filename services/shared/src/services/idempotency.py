import threading
import time

class AlreadyProcessed(Exception): pass

class IdempotencyGuard:
    def __init__(self, store: "IdempotencyStore", key: str):
        self.store = store
        self.key   = key

    def __enter__(self) -> "IdempotencyGuard":
        with self.store.lock:
            expiry = self.store.completed.get(self.key)
            if expiry is not None and time.monotonic() < expiry:
                raise AlreadyProcessed()
            self.store.completed[self.key] = time.monotonic() + self.store.ttl
        return self

    def __exit__(self, exc_type, *args) -> bool:
        if exc_type is AlreadyProcessed:
            return True  # suppress — already done, skip silently
        if exc_type is None:
            with self.store.lock:
                self.store.completed.pop(self.key, None)
        return False  # propagate any real exceptions

class IdempotencyStore:
    def __init__(
        self,
        ttl: float,
        cleanup_interval: float | None = None,
    ):
        self.completed: dict[str, float] = {}   # key → expiry monotonic time
        self.lock = threading.Lock()
        self.ttl  = ttl
        self.cleanup_interval = (
            cleanup_interval if cleanup_interval is not None
            else max(ttl / 2, 1)
        )
        self.start_cleanup_thread()

    def start_cleanup_thread(self) -> None:
        t = threading.Thread(target=self.cleanup_loop, daemon=True)
        t.name = "idempotency-cleanup"
        t.start()

    def cleanup_loop(self) -> None:
        while True:
            time.sleep(self.cleanup_interval)
            self.purge_expired()

    def purge_expired(self) -> int:
        now = time.monotonic()
        with self.lock:
            expired = [k for k, exp in self.completed.items() if exp <= now]
            for k in expired:
                del self.completed[k]
        return len(expired)

    def guard(self, *parts: str) -> IdempotencyGuard:
        return IdempotencyGuard(self, ":".join(parts))

    def __len__(self) -> int:
        with self.lock:
            return len(self.completed)