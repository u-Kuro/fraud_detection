from datetime import datetime

import pytest
from pydantic import ValidationError

from services.archive.src.modules.environment.archive import ArchiveEnvironment

def test_archive_environment_reads_cutoff(monkeypatch):
    monkeypatch.setenv(
        "TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF",
        "2025-06-01T00:00:00+00:00",
    )
    env = ArchiveEnvironment()
    assert isinstance(env.TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF, datetime)

def test_archive_environment_missing_cutoff_raises(monkeypatch):
    monkeypatch.delenv("TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF", raising=False)
    with pytest.raises(ValidationError):
        ArchiveEnvironment()

def test_archive_environment_parses_iso_datetime(monkeypatch):
    monkeypatch.setenv(
        "TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF",
        "2025-01-15T12:30:00+00:00",
    )
    env = ArchiveEnvironment()
    dt = env.TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF
    assert dt.year == 2025
    assert dt.month == 1
    assert dt.day == 15

def test_archive_environment_module_level_instance():
    from services.archive.src.modules.environment.archive import archive_environment
    assert isinstance(archive_environment, ArchiveEnvironment)
