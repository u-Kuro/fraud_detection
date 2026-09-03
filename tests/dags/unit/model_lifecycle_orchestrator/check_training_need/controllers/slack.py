from uuid import uuid4

from dags.model_lifecycle_orchestrator.check_training_need.controllers.slack import build_training_approval_blocks, build_training_approval_blocks_initializing, cold_start_buttons, drift_retraining_buttons

from unittest.mock import MagicMock

def test_cold_start_buttons_returns_list():
    buttons = cold_start_buttons(workflow_id=uuid4(), should_train_for_promotion=True)
    assert isinstance(buttons, list)

def test_cold_start_buttons_has_two_buttons():
    buttons = cold_start_buttons(workflow_id=uuid4(), should_train_for_promotion=False)
    assert len(buttons) == 2

def test_cold_start_buttons_action_ids():
    buttons = cold_start_buttons(workflow_id=uuid4(), should_train_for_promotion=True)
    action_ids = {b["action_id"] for b in buttons}
    assert "approve_training" in action_ids
    assert "reject_training" in action_ids

def test_drift_retraining_buttons_returns_list():
    buttons = drift_retraining_buttons(workflow_id=uuid4(), should_train_for_promotion=True)
    assert isinstance(buttons, list)

def test_drift_retraining_buttons_action_ids():
    buttons = drift_retraining_buttons(workflow_id=uuid4(), should_train_for_promotion=False)
    action_ids = {b["action_id"] for b in buttons}
    assert "approve_retraining" in action_ids
    assert "reject_retraining" in action_ids

def test_build_training_approval_blocks_no_drift_returns_list():
    blocks = build_training_approval_blocks(
        workflow_id=uuid4(),
        drift_result=None,
        should_train_for_promotion=True,
    )
    assert isinstance(blocks, list)

def test_build_training_approval_blocks_no_drift_has_header():
    blocks = build_training_approval_blocks(
        workflow_id=uuid4(),
        drift_result=None,
        should_train_for_promotion=True,
    )
    headers = [b for b in blocks if b.get("type") == "header"]
    assert len(headers) == 1
    assert "Training" in headers[0]["text"]["text"]

def test_build_training_approval_blocks_with_drift():
    mock_drift = MagicMock()
    mock_drift.drift_summary = {
        "data_drift": {"share_drifted_features": 0.5, "number_of_drifted_features": 5, "total_features": 10},
        "concept_drift": {"f1_delta": -0.1},
    }
    blocks = build_training_approval_blocks(
        workflow_id=uuid4(),
        drift_result=mock_drift,
        should_train_for_promotion=False,
    )
    assert isinstance(blocks, list)
    headers = [b for b in blocks if b.get("type") == "header"]
    assert "Retraining" in headers[0]["text"]["text"]

def test_build_training_approval_blocks_initializing_no_drift():
    blocks = build_training_approval_blocks_initializing(drift_result=None)
    assert isinstance(blocks, list)
    headers = [b for b in blocks if b.get("type") == "header"]
    assert len(headers) == 1

def test_build_training_approval_blocks_initializing_with_drift():
    mock_drift = MagicMock()
    mock_drift.drift_summary = {
        "data_drift": {"share_drifted_features": 0.3, "number_of_drifted_features": 3, "total_features": 10},
        "concept_drift": {"f1_delta": -0.08},
    }
    blocks = build_training_approval_blocks_initializing(drift_result=mock_drift)
    assert isinstance(blocks, list)
    assert len(blocks) > 0
