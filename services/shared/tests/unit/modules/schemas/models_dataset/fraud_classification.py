from enum import StrEnum

from services.shared.src.modules.schemas.models_dataset.fraud_classification import FraudClassificationFeaturesKeys
from services.shared.src.modules.schemas.postgres.transaction_inferences import TransactionInferences

def test_fraud_classification_features_keys_is_str_enum():
    assert issubclass(FraudClassificationFeaturesKeys, StrEnum)

def test_fraud_classification_features_keys_has_transaction_timestamp():
    assert FraudClassificationFeaturesKeys.transaction_timestamp == "transaction_timestamp"

def test_fraud_classification_features_keys_has_amount():
    assert FraudClassificationFeaturesKeys.amount == "amount"

def test_fraud_classification_features_keys_has_all_v_columns():
    keys = set(FraudClassificationFeaturesKeys)
    for i in range(1, 29):
        assert f"v{i}" in keys, f"Missing v{i} key"

def test_fraud_classification_features_keys_match_transaction_inferences_columns():
    for key in FraudClassificationFeaturesKeys:
        assert hasattr(TransactionInferences, key), f"Column {key} not in TransactionInferences"

def test_fraud_classification_features_keys_total_count():
    # transaction_timestamp + amount + v1..v28 = 30
    assert len(list(FraudClassificationFeaturesKeys)) == 30
