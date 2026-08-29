from dataclasses import dataclass

@dataclass(frozen=True)
class ArchiveKeys:
    TRANSACTION_INFERENCES_ARCHIVE_CUTOFF_ISO_DATETIME: str = "TRANSACTION_INFERENCES_ARCHIVE_CUTOFF_ISO_DATETIME"