import io

from evidently import DataDefinition, BinaryClassification, Dataset, Report
from evidently.presets import DataDriftPreset, ClassificationPreset
from pandas import DataFrame

from shared.modules.configs import fraud_classifier_config

def run_drift_report(
    df_reference: DataFrame,
    df_current: DataFrame
) -> tuple[dict, bytes]:
    """Run evidently report, return (summary_dict, html_bytes)."""
    data_definition = DataDefinition(
        classification=[BinaryClassification(
            target=fraud_classifier_config.FRAUD_CLASSIFIER_LABEL,
            prediction_labels=fraud_classifier_config.FRAUD_CLASSIFIER_PREDICTION_LABEL,
            prediction_probas=fraud_classifier_config.FRAUD_CLASSIFIER_PROBABILITY_LABEL,
            labels={0: "Legitimate", 1: "Fraud"},
        )],
        numerical_columns=fraud_classifier_config.FRAUD_CLASSIFIER_FEATURES,
    )
    reference_dataset = Dataset.from_pandas(
        data=df_reference,
        data_definition=data_definition
    )
    current_dataset = Dataset.from_pandas(
        data=df_current,
        data_definition=data_definition
    )
    report = Report(
        metrics=[
            DataDriftPreset(),
            ClassificationPreset()
        ]
    )
    result = report.run(
        reference_data=reference_dataset,
        current_data=current_dataset
    )
    buffer = io.StringIO()
    result.save_html(buffer)
    summary = extract_drift_summary(
        result.dict(),
        fraud_classifier_config.FRAUD_CLASSIFIER_FEATURES
    )
    return summary, buffer.getvalue().encode("utf-8")

def extract_drift_summary(
    results: dict,
    feature_columns: list[str]
) -> dict:
    data_drift: dict = {}
    concept_drift: dict = {}

    for metric in results.get("metrics", []):
        metric_name = metric.get("metric", "")
        result = metric.get("result", {})

        # Data drift — feature distribution shift P(X)
        if "drift_by_columns" in result:
            drifted = [
                col
                for col, info in result["drift_by_columns"].items()
                if col in feature_columns and info.get("drift_detected", False)
            ]
            data_drift = {
                "dataset_drift_detected": result.get("dataset_drift", False),
                "share_drifted_features": result.get("share_drifted_features", 0.0),
                "number_of_drifted_features": result.get("number_of_drifted_features", 0),
                "total_features": result.get("number_of_columns", len(feature_columns)),
                "drifted_feature_names": drifted,
            }

        # Concept / model performance drift — P(Y|X) degradation
        if metric_name == "ClassificationQualityMetric" and "current" in result and "reference" in result:
            cur = result["current"]
            ref = result["reference"]

            def delta(key: str) -> float | None:
                c, r = cur.get(key), ref.get(key)
                return round(c - r, 4) if c is not None and r is not None else None

            f1_delta = delta("f1")
            concept_drift = {
                "f1_current": cur.get("f1"),
                "f1_reference": ref.get("f1"),
                "f1_delta": delta("f1"),
                "roc_auc_current": cur.get("roc_auc"),
                "roc_auc_reference": ref.get("roc_auc"),
                "roc_auc_delta": delta("roc_auc"),
                "precision_delta": delta("precision"),
                "recall_delta": delta("recall"),
                # A negative delta means the model performs worse on current data.
                # Flag concept drift if F1 degrades by more than 5 pp.
                "concept_drift_detected": f1_delta is not None and f1_delta < -0.05
            }

    return {
        # Data drift (P(X) shift)
        "data_drift": data_drift,
        # Concept drift (P(Y|X) shift: model quality on current data vs reference)
        "concept_drift": concept_drift,
    }