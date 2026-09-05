from datetime import datetime

from _pytest.monkeypatch import MonkeyPatch

from services.archive.src.modules.environment.archive import ArchiveEnvironment

class TestArchiveEnvironment:
    def test_instance(self):
        from services.archive.src.modules.environment.archive import archive_environment
        assert isinstance(archive_environment, ArchiveEnvironment)

    def test_values(self, monkeypatch: MonkeyPatch):
        value = datetime.now()
        monkeypatch.setenv(
            name="TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF",
            value=value.isoformat(),
        )

        environment = ArchiveEnvironment()

        assert environment.TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF == value