from uuid import uuid4

import pytest
from pydantic import ValidationError

from services.fraud_detection.src.modules.schemas.slack import PromotionValue, TrainingValue

def test_training_value_instantiation():
    wid = uuid4()
    tv = TrainingValue(workflow_id=wid, should_train_for_promotion=True)
    assert tv.workflow_id == wid
    assert tv.should_train_for_promotion is True

def test_training_value_should_train_for_promotion_strict_bool():
    wid = uuid4()
    with pytest.raises(ValidationError):
        TrainingValue(workflow_id=wid, should_train_for_promotion=1)

def test_promotion_value_instantiation():
    wid = uuid4()
    pv = PromotionValue(workflow_id=wid)
    assert pv.workflow_id == wid

def test_promotion_value_missing_workflow_id_raises():
    with pytest.raises(ValidationError):
        PromotionValue()

def test_training_value_json_round_trip():
    wid = uuid4()
    tv = TrainingValue(workflow_id=wid, should_train_for_promotion=False)
    restored = TrainingValue.model_validate_json(tv.model_dump_json())
    assert restored.workflow_id == wid
    assert restored.should_train_for_promotion is False
