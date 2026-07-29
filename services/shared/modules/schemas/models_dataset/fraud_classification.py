from enum import StrEnum

from services.shared.modules.schemas.postgres.transaction_inferences import TransactionInference

class FraudClassificationFeaturesKeys(StrEnum):
    transaction_timestamp = TransactionInference.transaction_timestamp.key
    amount = TransactionInference.amount.key
    v1 = TransactionInference.v1.key
    v2 = TransactionInference.v2.key
    v3 = TransactionInference.v3.key
    v4 = TransactionInference.v4.key
    v5 = TransactionInference.v5.key
    v6 = TransactionInference.v6.key
    v7 = TransactionInference.v7.key
    v8 = TransactionInference.v8.key
    v9 = TransactionInference.v9.key
    v10 = TransactionInference.v10.key
    v11 = TransactionInference.v11.key
    v12 = TransactionInference.v12.key
    v13 = TransactionInference.v13.key
    v14 = TransactionInference.v14.key
    v15 = TransactionInference.v15.key
    v16 = TransactionInference.v16.key
    v17 = TransactionInference.v17.key
    v18 = TransactionInference.v18.key
    v19 = TransactionInference.v19.key
    v20 = TransactionInference.v20.key
    v21 = TransactionInference.v21.key
    v22 = TransactionInference.v22.key
    v23 = TransactionInference.v23.key
    v24 = TransactionInference.v24.key
    v25 = TransactionInference.v25.key
    v26 = TransactionInference.v26.key
    v27 = TransactionInference.v27.key
    v28 = TransactionInference.v28.key