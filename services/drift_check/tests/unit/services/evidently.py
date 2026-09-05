from unittest.mock import MagicMock

from pandas import DataFrame
from pytest_mock import MockerFixture

from services.drift_check.src.modules.configs.evidently import EvidentlyConfig
from services.drift_check.src.services.evidently import run_drift_report, extract_drift_summary
from services.shared.src.modules.schemas.models_dataset.fraud_classification import FraudClassificationFeaturesKeys
from services.shared.src.modules.schemas.postgres.transaction_inferences import TransactionInferences

def test_run_drift_report(mocker: MockerFixture):
    df = DataFrame({
        TransactionInferences.is_fraud.key: [1.0],
        TransactionInferences.is_fraud_prediction.key: [1],
        TransactionInferences.is_fraud_probability.key: [1.0],
        TransactionInferences.amount.key: [1.0],
        TransactionInferences.transaction_timestamp.key: [1],
        **{key: [1.0] for key in FraudClassificationFeaturesKeys},
    })
    mocker.patch.object(df[TransactionInferences.is_fraud.key], "count", return_value=DatasetConfig.minimum_rows)

    mock_result = MagicMock()
    mock_result.dict.return_value = {"metrics": []}
    mocker.patch(
        "services.drift_check.src.repositories.evidently.drift_report.Report",
        return_value=MagicMock(run=MagicMock(return_value=mock_result))
    )
    mocker.patch(
        "services.drift_check.src.repositories.evidently.drift_report.extract_drift_summary",
        return_value={"data_drift": {}, "concept_drift": {}}
    )

    summary, html_bytes = run_drift_report(df, df)

    assert isinstance(summary, dict)
    assert isinstance(html_bytes, bytes)


def test_extract_drift_summary():
    results = {
        "metrics": [
            {
                "metric": "DataDriftPreset",
                "result": {
                    "drift_by_columns": {
                        "v1": {"drift_detected": True},
                    },
                    "share_drifted_features": 1.0,
                    "number_of_drifted_features": 1,
                    "number_of_columns": 1,
                    "dataset_drift": True,
                }
            },
            {
                "metric": "ClassificationQualityMetric",
                "result": {
                    "current": {"f1": 0.80, "roc_auc": 0.85, "precision": 0.78, "recall": 0.82},
                    "reference": {"f1": 0.90, "roc_auc": 0.92, "precision": 0.88, "recall": 0.91},
                }
            }
        ]
    }

    summary = extract_drift_summary(results=results, feature_names={"v1"})

    data_drift = summary[EvidentlyConfig.data_drift_key]
    assert data_drift["drifted_feature_names"] == ["v1"]
    assert data_drift[EvidentlyConfig.drifted_key] is True

    concept_drift = summary[EvidentlyConfig.concept_drift_key]
    assert concept_drift["f1_delta"] == round(0.80 - 0.90, 4)
    assert concept_drift[EvidentlyConfig.drifted_key] is True
