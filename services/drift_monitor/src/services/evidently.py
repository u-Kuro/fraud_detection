import io

from evidently import DataDefinition, BinaryClassification, Dataset, Report
from evidently.presets import DataDriftPreset, ClassificationPreset
from pandas import DataFrame

from shared.modules.schemas import FraudClassifierFeatures, FraudClassifierLabel, FraudClassificationPrediction, \
    FraudClassificationProbability


def run_drift_report(
    df_reference: DataFrame,
    df_current: DataFrame
) -> tuple[dict, bytes]:
    data_definition = DataDefinition(
        classification=[BinaryClassification(
            target=FraudClassifierLabel.model_field_key(),
            prediction_labels=FraudClassificationPrediction.model_field_key(),
            prediction_probas=FraudClassificationProbability.model_field_key(),
            labels={0: "Legitimate", 1: "Fraud"},
        )],
        numerical_columns=FraudClassifierFeatures.model_field_keys(),
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
        set(FraudClassifierFeatures.model_field_keys())
    )
    return summary, buffer.getvalue().encode("utf-8")

def extract_drift_summary(
    results: dict,
    feature_names: set[str]
) -> dict:
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
                "dataset_drift_detected": result.get("dataset_drift", False),
                "share_drifted_features": result.get("share_drifted_features", 0.0),
                "number_of_drifted_features": result.get("number_of_drifted_features", 0),
                "total_features": result.get("number_of_columns", len(feature_names)),
                "drifted_feature_names": drifted_feature_names,
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
                "concept_drift_detected": f1_delta is not None and f1_delta < -0.05
            }

    return {
        # Data drift (P(X) shift)
        "data_drift": data_drift,
        # Concept drift (P(Y|X) shift: model quality on current data vs reference)
        "concept_drift": concept_drift,
    }