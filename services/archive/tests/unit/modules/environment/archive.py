from datetime import datetime

import pytest
from _pytest.monkeypatch import MonkeyPatch
from pydantic import ValidationError

from services.archive.src.modules.environment.archive import ArchiveEnvironment

def test_archive_environment_module_level_instance():
    from services.archive.src.modules.environment.archive import archive_environment
    assert isinstance(archive_environment, ArchiveEnvironment)

def test_archive_environment_reads_cutoff(monkeypatch: MonkeyPatch):
    monkeypatch.setenv(
        "TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF",
        datetime.now().isoformat(),
    )
    environment = ArchiveEnvironment()
    assert isinstance(environment.TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF, datetime)

def test_archive_environment_raises_missing_cutoff(monkeypatch: MonkeyPatch):
    monkeypatch.delenv("TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF", raising=False)
    with pytest.raises(ValidationError):
        ArchiveEnvironment()