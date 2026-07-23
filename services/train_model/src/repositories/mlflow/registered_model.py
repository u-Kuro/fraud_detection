import mlflow
from mlflow.models import infer_signature
from numpy import ndarray

from services.shared.modules.configs import MLFlowConfig
from services.train_model.src.modules.schemas.mlflow import MLFlowRegisteredModelInfo

def save_and_register_model(
    model: object,
    X_test_samples: ndarray,
) -> MLFlowRegisteredModelInfo:
    model_info = mlflow.sklearn.log_model(
        sk_model=model,
        serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_SKOPS,
        registered_model_name=MLFlowConfig.MODEL_NAME,
        signature=infer_signature(
            model_input=X_test_samples,
            model_output=model.predict(X_test_samples)
        ),
        input_example=X_test_samples,
        pip_requirements=[
            "xgboost==3.2.0",
            "scikit-learn==1.8.0",
            "numpy==2.4.6",
            "pandas==2.3.3",
        ],
        name=MLFlowConfig.MODEL_PATH,
        skops_trusted_types=[
            "xgboost.core.Booster",
            "xgboost.sklearn.XGBClassifier",
        ],
    )

    if isinstance(model_info.registered_model_version, int):
        return MLFlowRegisteredModelInfo(
            run_id=model_info.run_id,
            model_id=model_info.model_id,
            model_name=MLFlowConfig.MODEL_NAME,
            model_version=model_info.registered_model_version
        )
    else:
        raise RuntimeError("Model registration failed: registered_model_version is not an integer.")



