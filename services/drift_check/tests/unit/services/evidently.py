import pandas
from pytest_mock import MockerFixture

from services.drift_check.src.modules.configs.evidently import EvidentlyConfig
from services.drift_check.src.services.evidently import extract_drift_summary, run_drift_report
from services.shared.src.modules.schemas.models_dataset.fraud_classification import FraudClassificationFeaturesKeys
from services.shared.src.modules.schemas.postgres.transaction_inferences import TransactionInferences

def test_extract_drift_summary():
    feature_name = "feature"
    summary = extract_drift_summary(
        results={
            "metrics": [
                {
                    "metric": "DataDriftPreset",
                    "result": {
                        "drift_by_columns": {
                            feature_name: { "drift_detected": True },
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
                        "current": { "f1": 1.0 },
                        "reference": { "f1": 0.0 },
                    }
                }
            ]
        },
        feature_names={ feature_name }
    )

    assert EvidentlyConfig.data_drift_key in summary
    assert EvidentlyConfig.concept_drift_key in summary

    data_drift = summary[EvidentlyConfig.data_drift_key]
    assert EvidentlyConfig.drifted_key in data_drift

    concept_drift = summary[EvidentlyConfig.concept_drift_key]
    assert EvidentlyConfig.drifted_key in concept_drift

def test_run_drift_report(mocker: MockerFixture):
    dataframe = pandas.DataFrame({
        TransactionInferences.is_fraud.key: [1.0],
        TransactionInferences.is_fraud_prediction.key: [1],
        TransactionInferences.is_fraud_probability.key: [1.0],
        **{key: [1.0] for key in FraudClassificationFeaturesKeys},
        TransactionInferences.transaction_timestamp.key: [1],
    })
    mocker.patch.object(dataframe[TransactionInferences.is_fraud.key], "count", return_value=DatasetConfig.minimum_rows)

    summary, html_bytes = run_drift_report(dataframe, dataframe)

    assert isinstance(summary, dict)
    assert isinstance(html_bytes, bytes)