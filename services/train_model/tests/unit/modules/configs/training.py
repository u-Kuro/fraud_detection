import dataclasses

import pytest

from services.train_model.src.modules.configs.training import TrainingConfig


def test_training_config_random_state():
    assert TrainingConfig.random_state == 42


def test_training_config_test_size():
    assert TrainingConfig.test_size == 0.2


def test_training_config_bayes_steps():
    assert TrainingConfig.bayes_steps == 30


def test_training_config_timeout_positive():
    assert TrainingConfig.training_timeout_seconds > 0


def test_training_config_is_frozen():
    config = TrainingConfig()
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        config.random_state = 0


def test_cv_val_size_classmethod():
    # 0.2 / (1 - 0.2) = 0.25
    result = TrainingConfig.cv_val_size()
    assert abs(result - 0.25) < 1e-9


def test_cv_val_size_between_zero_and_one():
    result = TrainingConfig.cv_val_size()
    assert 0 < result < 1
