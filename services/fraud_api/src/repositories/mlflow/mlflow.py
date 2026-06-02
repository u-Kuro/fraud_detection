import mlflow
from mlflow import MlflowClient
from services.fraud_api.src.modules.environment import environment

mlflow.set_tracking_uri(environment.MLFLOW_TRACKING_URI)
client: MlflowClient = MlflowClient()