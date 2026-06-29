import threading

class AlreadyProcessed(Exception): pass

class IdempotencyGuard:
    def __init__(self, store: "IdempotencyStore", key: str):
        self.store = store
        self.key   = key

    def __enter__(self) -> "IdempotencyGuard":
        with self.store.lock:
            if self.key in self.store.completed:
                raise AlreadyProcessed()
        return self

    def __exit__(self, exc_type, *args) -> bool:
        if exc_type is AlreadyProcessed:
            return True  # suppress — already done, skip silently
        if exc_type is None:
            with self.store.lock:
                self.store.completed.add(self.key)
        return False  # propagate any real exceptions

class IdempotencyStore:
    def __init__(self):
        self.completed: set[str] = set()
        self.lock = threading.Lock()

    def guard(self, *parts: str) -> IdempotencyGuard:
        return IdempotencyGuard(self, ":".join(parts))

slack_action_store = IdempotencyStore()