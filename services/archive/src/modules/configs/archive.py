from dataclasses import dataclass

@dataclass(frozen=True)
class ArchiveConfig:
    batch_size: int = 50_000