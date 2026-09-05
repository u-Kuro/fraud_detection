from datetime import datetime

import pytest
from _pytest.monkeypatch import MonkeyPatch
from pydantic import ValidationError

from services.archive.src.modules.environment.archive import ArchiveEnvironment

def test_archive_environment_instance():
    from services.archive.src.modules.environment.archive import archive_environment
    assert isinstance(archive_environment, ArchiveEnvironment)

def test_archive_environment_values(monkeypatch: MonkeyPatch):
    value = datetime.now()
    monkeypatch.setenv(
        name="TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF",
        value=value.isoformat(),
    )

    environment = ArchiveEnvironment()

    assert isinstance(environment.TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF, datetime)
    assert environment.TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF == value

def test_archive_environment_failure_with_missing_environment(monkeypatch: MonkeyPatch):
    monkeypatch.delenv(
        name="TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF",
        raising=False
    )

    with pytest.raises(ValidationError):
        ArchiveEnvironment()