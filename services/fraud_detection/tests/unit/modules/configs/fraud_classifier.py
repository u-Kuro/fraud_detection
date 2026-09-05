from pytest_mock import MockerFixture

from services.fraud_detection.src.modules.configs.fraud_classifier import FraudClassifierConfig
from services.fraud_detection.src.modules.schemas.mlflow import DeployedModel

class TestFraudClassifierConfig:
    def test_values(self, mocker: MockerFixture):
        deployed_model_value = DeployedModel(
            model_name="model",
            model_version=1,
        )
        mocker.patch(
            target="services.fraud_detection.src.repositories.postgres.model_deployments.get_active_model_deployment",
            return_value=deployed_model_value,
        )
        FraudClassifierConfig.deployed_model.cache_clear()

        deployed_model_result = FraudClassifierConfig.deployed_model()

        assert isinstance(FraudClassifierConfig.classification_threshold, float)
        assert isinstance(deployed_model_result, DeployedModel)

        assert 1.0 > FraudClassifierConfig.classification_threshold > 0.0
        assert deployed_model_result == deployed_model_value