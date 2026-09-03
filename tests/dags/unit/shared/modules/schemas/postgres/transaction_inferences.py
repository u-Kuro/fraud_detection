from dags.shared.modules.schemas.postgres.transaction_inferences import TransactionInferences

def test_transaction_inferences_tablename():
    assert TransactionInferences.__tablename__ == "transaction_inferences"

def test_transaction_inferences_has_amount():
    assert hasattr(TransactionInferences, "amount")

def test_transaction_inferences_has_is_fraud():
    assert hasattr(TransactionInferences, "is_fraud")
