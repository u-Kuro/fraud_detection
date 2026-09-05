from _pytest.monkeypatch import MonkeyPatch

from services.drift_check.src.modules.environment.drift_check import DriftCheckEnvironment

class TestDriftCheckEnvironment:
    def test_instance(self):
        from services.drift_check.src.modules.environment.drift_check import drift_check_environment

        assert isinstance(drift_check_environment, DriftCheckEnvironment)

    def test_values(self, monkeypatch: MonkeyPatch):
        value = "value"
        monkeypatch.setenv(
            name="ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID",
            value=value
        )

        environment = DriftCheckEnvironment()

        assert environment.ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID == value