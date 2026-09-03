import pytest
from pydantic import ValidationError

from services.fraud_detection.src.modules.schemas.status import StatusResponse

def test_status_response_instantiation():
    resp = StatusResponse(status="ok")
    assert resp.status == "ok"

def test_status_response_status_must_be_strict_str():
    with pytest.raises(ValidationError):
        StatusResponse(status=42)

def test_status_response_any_string():
    resp = StatusResponse(status="error")
    assert resp.status == "error"
