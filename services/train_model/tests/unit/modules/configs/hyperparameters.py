from unittest.mock import MagicMock
import dataclasses

import pytest

from services.train_model.src.modules.configs.hyperparameters import XGBHyperparametersSampler


def test_xgb_sampler_is_frozen_dataclass():
    sampler = XGBHyperparametersSampler()
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        sampler.n_estimators = None


def test_xgb_sampler_resolve_returns_dict():
    sampler = XGBHyperparametersSampler()
    mock_trial = MagicMock()
    mock_trial.suggest_int.return_value = 100
    mock_trial.suggest_float.return_value = 0.1
    result = sampler.resolve(mock_trial)
    assert isinstance(result, dict)


def test_xgb_sampler_resolve_contains_n_estimators():
    sampler = XGBHyperparametersSampler()
    mock_trial = MagicMock()
    mock_trial.suggest_int.return_value = 200
    mock_trial.suggest_float.return_value = 0.1
    result = sampler.resolve(mock_trial)
    assert "n_estimators" in result


def test_xgb_sampler_resolve_contains_all_hyperparams():
    sampler = XGBHyperparametersSampler()
    mock_trial = MagicMock()
    mock_trial.suggest_int.return_value = 100
    mock_trial.suggest_float.return_value = 0.1
    result = sampler.resolve(mock_trial)
    expected_keys = {
        "n_estimators", "max_depth", "learning_rate", "subsample",
        "colsample_bytree", "reg_alpha", "reg_lambda", "gamma", "min_child_weight"
    }
    assert expected_keys == set(result.keys())


def test_xgb_sampler_resolve_calls_trial_suggest():
    sampler = XGBHyperparametersSampler()
    mock_trial = MagicMock()
    mock_trial.suggest_int.return_value = 100
    mock_trial.suggest_float.return_value = 0.1
    sampler.resolve(mock_trial)
    assert mock_trial.suggest_int.call_count >= 1
    assert mock_trial.suggest_float.call_count >= 1
