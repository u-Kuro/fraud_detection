from services.shared.src.modules.schemas.postgres.transaction_inferences import TransactionInferences

def test_transaction_inferences_tablename():
    assert TransactionInferences.__tablename__ == "transaction_inferences"

def test_transaction_inferences_has_all_v_columns():
    for i in range(1, 29):
        assert hasattr(TransactionInferences, f"v{i}"), f"Missing v{i} column"

def test_transaction_inferences_has_transaction_id():
    assert hasattr(TransactionInferences, "transaction_id")

def test_transaction_inferences_has_amount():
    assert hasattr(TransactionInferences, "amount")

def test_transaction_inferences_has_is_fraud():
    assert hasattr(TransactionInferences, "is_fraud")

def test_transaction_inferences_has_is_fraud_prediction():
    assert hasattr(TransactionInferences, "is_fraud_prediction")

def test_transaction_inferences_has_is_fraud_probability():
    assert hasattr(TransactionInferences, "is_fraud_probability")

def test_transaction_inferences_has_model_deployment_id():
    assert hasattr(TransactionInferences, "model_deployment_id")

def test_transaction_inferences_has_transaction_timestamp():
    assert hasattr(TransactionInferences, "transaction_timestamp")

def test_transaction_inferences_column_keys_are_strings():
    assert isinstance(TransactionInferences.amount.key, str)
    assert isinstance(TransactionInferences.is_fraud.key, str)
