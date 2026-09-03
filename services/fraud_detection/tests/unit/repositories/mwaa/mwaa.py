from services.fraud_detection.src.repositories.mwaa.mwaa import mwaa_client

def test_mwaa_client_is_not_none():
    assert mwaa_client is not None

def test_mwaa_client_has_invoke_rest_api():
    assert hasattr(mwaa_client, "invoke_rest_api")
