from unittest.mock import MagicMock

import pandas as pd

from services.drift_check.src.services.evidently import drift_check, extract_drift_summary

def test_extract_drift_summary_returns_both_keys():
    summary = extract_drift_summary(results={}, feature_names=set())
    assert "data_drift" in summary
    assert "concept_drift" in summary

def test_extract_drift_summary_empty_results():
    summary = extract_drift_summary(results={"metrics": []}, feature_names={"v1"})
    assert summary["data_drift"] == {}
    assert summary["concept_drift"] == {}

def test_extract_drift_summary_parses_data_drift():
    results = {
        "metrics": [
            {
                "metric": "DataDriftPreset",
                "result": {
                    "drift_by_columns": {
                        "v1": {"drift_detected": True},
                        "v2": {"drift_detected": False},
                    },
                    "share_drifted_features": 0.5,
                    "number_of_drifted_features": 1,
                    "number_of_columns": 2,
                    "dataset_drift": True,
                },
            }
        ]
    }
    summary = extract_drift_summary(results=results, feature_names={"v1", "v2"})
    data = summary["data_drift"]
    assert data["share_drifted_features"] == 0.5
    assert data["number_of_drifted_features"] == 1
    assert data["drifted"] is True
    assert "v1" in data["drifted_feature_names"]
    assert "v2" not in data["drifted_feature_names"]

def test_extract_drift_summary_parses_concept_drift():
    results = {
        "metrics": [
            {
                "metric": "ClassificationQualityMetric",
                "result": {
                    "current": {"f1": 0.7, "roc_auc": 0.85, "precision": 0.75, "recall": 0.65},
                    "reference": {"f1": 0.8, "roc_auc": 0.9, "precision": 0.8, "recall": 0.8},
                },
            }
        ]
    }
    summary = extract_drift_summary(results=results, feature_names=set())
    concept = summary["concept_drift"]
    assert concept["f1_delta"] == round(0.7 - 0.8, 4)
    assert concept["drifted"] is True  # f1_delta < -0.05

def test_extract_drift_summary_concept_drift_not_drifted_when_small_drop():
    results = {
        "metrics": [
            {
                "metric": "ClassificationQualityMetric",
                "result": {
                    "current": {"f1": 0.79, "roc_auc": 0.9, "precision": 0.8, "recall": 0.78},
                    "reference": {"f1": 0.8, "roc_auc": 0.9, "precision": 0.8, "recall": 0.8},
                },
            }
        ]
    }
    summary = extract_drift_summary(results=results, feature_names=set())
    assert summary["concept_drift"]["drifted"] is False

def test_extract_drift_summary_ignores_non_feature_columns():
    results = {
        "metrics": [
            {
                "metric": "DataDriftPreset",
                "result": {
                    "drift_by_columns": {
                        "is_fraud": {"drift_detected": True},
                    },
                    "share_drifted_features": 1.0,
                    "number_of_drifted_features": 1,
                    "number_of_columns": 1,
                    "dataset_drift": True,
                },
            }
        ]
    }
    # is_fraud is not in feature_names
    summary = extract_drift_summary(results=results, feature_names={"v1"})
    assert "is_fraud" not in summary["data_drift"].get("drifted_feature_names", [])

def test_drift_check_returns_bool_and_dict(mocker):
    mock_ref_df = pd.DataFrame()
    mocker.patch(
        "services.drift_check.src.services.evidently.load_reference_dataset",
        return_value=(mock_ref_df, MagicMock()),
    )
    mocker.patch(
        "services.drift_check.src.services.evidently.load_current_dataset",
        return_value=pd.DataFrame(),
    )
    mocker.patch(
        "services.drift_check.src.services.evidently.run_drift_report",
        return_value=(
            {"data_drift": {"drifted": True}, "concept_drift": {"drifted": False}},
            b"<html/>",
        ),
    )
    mocker.patch("services.drift_check.src.services.evidently.upload_drift_report")

    detected, summary = drift_check()
    assert isinstance(detected, bool)
    assert isinstance(summary, dict)

def test_drift_check_detected_true_when_data_drift(mocker):
    mocker.patch(
        "services.drift_check.src.services.evidently.load_reference_dataset",
        return_value=(pd.DataFrame(), MagicMock()),
    )
    mocker.patch(
        "services.drift_check.src.services.evidently.load_current_dataset",
        return_value=pd.DataFrame(),
    )
    mocker.patch(
        "services.drift_check.src.services.evidently.run_drift_report",
        return_value=(
            {"data_drift": {"drifted": True}, "concept_drift": {"drifted": False}},
            b"<html/>",
        ),
    )
    mocker.patch("services.drift_check.src.services.evidently.upload_drift_report")

    detected, _ = drift_check()
    assert detected is True

def test_drift_check_detected_false_when_no_drift(mocker):
    mocker.patch(
        "services.drift_check.src.services.evidently.load_reference_dataset",
        return_value=(pd.DataFrame(), MagicMock()),
    )
    mocker.patch(
        "services.drift_check.src.services.evidently.load_current_dataset",
        return_value=pd.DataFrame(),
    )
    mocker.patch(
        "services.drift_check.src.services.evidently.run_drift_report",
        return_value=(
            {"data_drift": {"drifted": False}, "concept_drift": {"drifted": False}},
            b"<html/>",
        ),
    )
    mocker.patch("services.drift_check.src.services.evidently.upload_drift_report")

    detected, _ = drift_check()
    assert detected is False
