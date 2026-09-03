import pytest

from dags.shared.modules.utilities.airflow.airflow import sequence

from unittest.mock import MagicMock

def test_sequence_with_two_tasks_sets_dependency():
    t1, t2 = MagicMock(), MagicMock()
    sequence(t1, t2)
    t1.__rshift__.assert_called_once_with(t2)

def test_sequence_with_three_tasks_chains_dependencies():
    t1, t2, t3 = MagicMock(), MagicMock(), MagicMock()
    sequence(t1, t2, t3)
    t1.__rshift__.assert_called_once_with(t2)
    t2.__rshift__.assert_called_once_with(t3)

def test_sequence_returns_first_task():
    t1, t2, t3 = MagicMock(), MagicMock(), MagicMock()
    result = sequence(t1, t2, t3)
    assert result is t1

def test_sequence_with_single_task_returns_it():
    t1 = MagicMock()
    result = sequence(t1)
    assert result is t1
    t1.__rshift__.assert_not_called()

def test_sequence_asserts_non_empty():
    with pytest.raises(AssertionError):
        sequence()
