import io
import json

from evidently import DataDefinition, BinaryClassification, Dataset, Report
from evidently.presets import DataDriftPreset, ClassificationPreset
from pandas import DataFrame

from services.drift_check.src.modules.configs.evidently import EvidentlyConfig
from services.drift_check.src.repositories.mlflow.registered_model_dataset import load_reference_dataset
from services.drift_check.src.repositories.postgres.transaction_inferences import load_current_dataset
from services.drift_check.src.repositories.s3.drift_reports import upload_drift_report
from services.shared.src.modules.configs.dataset import DatasetConfig
from services.shared.src.modules.schemas.models_dataset.fraud_classification import FraudClassificationFeaturesKeys
from services.shared.src.modules.schemas.postgres.transaction_inferences import TransactionInferences

def run_drift_report(
    df_reference: DataFrame,
    df_current: DataFrame
) -> tuple[dict[str, dict], bytes]:
    data_definition = DataDefinition(
        classification=[BinaryClassification(
            target=TransactionInferences.is_fraud.key,
            prediction_labels=TransactionInferences.is_fraud_prediction.key,
            prediction_probas=TransactionInferences.is_fraud_probability.key,
            labels={0: "Legitimate", 1: "Fraud"},
        )],
        numerical_columns=list(FraudClassificationFeaturesKeys),
    )
    reference_dataset = Dataset.from_pandas(
        data=df_reference,
        data_definition=data_definition
    )
    current_dataset = Dataset.from_pandas(
        data=df_current,
        data_definition=data_definition
    )

    # Only include ClassificationPreset if there's enough labeled data
    # Fraud labels arrive earlier which skews concept drift
    metrics: list[DataDriftPreset | ClassificationPreset] = [DataDriftPreset()]
    if df_current[TransactionInferences.is_fraud.key].count() >= DatasetConfig.minimum_rows:
        metrics.append(ClassificationPreset())

    report = Report(
        metrics=metrics
    )
    result = report.run(
        reference_data=reference_dataset,
        current_data=current_dataset
    )
    buffer = io.StringIO()
    result.save_html(buffer)
    summary = extract_drift_summary(
        results=result.dict(),
        feature_names=set(FraudClassificationFeaturesKeys)
    )
    return summary, buffer.getvalue().encode("utf-8")

def extract_drift_summary(
    results: dict,
    feature_names: set[str]
) -> dict[str, dict]:
    data_drift: dict = {}
    concept_drift: dict = {}

    for metric in results.get("metrics", []):
        metric_name = metric.get("metric", "")
        result = metric.get("result", {})

        # Data drift — feature distribution shift P(X)
        if "drift_by_columns" in result:
            drifted_feature_names = [
                feature_name
                for feature_name, info in result["drift_by_columns"].items()
                if info.get("drift_detected", False) and feature_name in feature_names
            ]
            data_drift = {
                "share_drifted_features": result.get("share_drifted_features", 0.0),
                "number_of_drifted_features": result.get("number_of_drifted_features", 0),
                "total_features": result.get("number_of_columns", len(feature_names)),
                "drifted_feature_names": drifted_feature_names,
                EvidentlyConfig.drifted_key: result.get("dataset_drift", False),
            }

        # Concept / model performance drift — P(Y|X) degradation
        if metric_name == "ClassificationQualityMetric" and "current" in result and "reference" in result:
            current = result["current"]
            reference = result["reference"]

            def delta(key: str) -> float | None:
                c, r = current.get(key), reference.get(key)
                if c is None or r is None: return None
                else: return round(c - r, 4)

            f1_delta = delta("f1")
            concept_drift = {
                "f1_current": current.get("f1"),
                "f1_reference": reference.get("f1"),
                "f1_delta": f1_delta,
                "roc_auc_current": current.get("roc_auc"),
                "roc_auc_reference": reference.get("roc_auc"),
                "roc_auc_delta": delta("roc_auc"),
                "precision_delta": delta("precision"),
                "recall_delta": delta("recall"),
                # A negative delta means the model performs worse on current data.
                # Flag concept drift if F1 degrades by more than 5 pp.
                # TODO - idk if we need to remove or change this concept drift. I need to check it manually first online.
                EvidentlyConfig.drifted_key: f1_delta is not None and f1_delta < -0.05
            }

    return {
        # Data drift (P(X) shift)
        EvidentlyConfig.data_drift_key: data_drift,
        # Concept drift (P(Y|X) shift: model quality on current data vs reference)
        EvidentlyConfig.concept_drift_key: concept_drift,
    }

def drift_check() -> tuple[bool, dict[str, dict]]:
    df_reference, current_dataset_cutoff = load_reference_dataset()
    df_current = load_current_dataset(current_dataset_cutoff)

    drift_summary, html_bytes = run_drift_report(df_reference, df_current)
    upload_drift_report(html_bytes, json.dumps(drift_summary).encode())

    data_drift = drift_summary[EvidentlyConfig.data_drift_key].get(EvidentlyConfig.drifted_key, False)
    concept_drift = drift_summary[EvidentlyConfig.concept_drift_key].get(EvidentlyConfig.drifted_key, False)

    drift_detected = data_drift or concept_drift

    return drift_detected, drift_summary