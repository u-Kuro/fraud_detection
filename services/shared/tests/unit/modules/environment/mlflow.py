from _pytest.monkeypatch import MonkeyPatch

from services.shared.src.modules.environment.mlflow import MLflowEnvironment

class TestMLflowEnvironment:
    def test_instance(self):
        from services.shared.src.modules.environment.mlflow import mlflow_environment

        assert isinstance(mlflow_environment, MLflowEnvironment)

    def test_values(self, monkeypatch: MonkeyPatch):
        value = "value"
        monkeypatch.setenv(
            name="MLFLOW_WORKSPACE",
            value=value
        )

        environment = MLflowEnvironment()

        assert environment.MLFLOW_WORKSPACE == value