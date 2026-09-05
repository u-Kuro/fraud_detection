from services.fraud_detection.src.modules.schemas.mlflow import DeployedModel
from services.fraud_detection.src.repositories.mlflow.models import MlflowModel

class TestMlflowModel:
    @staticmethod
    def make_data():
        return {
            "deployed_model": DeployedModel(
                model_name="value",
                model_version=1
            )
        }

    def test_values(self):
        data = self.make_data()
        values = MlflowModel(**data)

        for key, expected in data.items():
            actual = getattr(values, key)

            assert expected == actual