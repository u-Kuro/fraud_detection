from enum import StrEnum

from services.shared.src.modules.schemas.postgres.transaction_inferences import TransactionInferences

class FraudClassificationFeaturesKeys(StrEnum):
    transaction_timestamp = TransactionInferences.transaction_timestamp.key
    amount = TransactionInferences.amount.key
    v1 = TransactionInferences.v1.key
    v2 = TransactionInferences.v2.key
    v3 = TransactionInferences.v3.key
    v4 = TransactionInferences.v4.key
    v5 = TransactionInferences.v5.key
    v6 = TransactionInferences.v6.key
    v7 = TransactionInferences.v7.key
    v8 = TransactionInferences.v8.key
    v9 = TransactionInferences.v9.key
    v10 = TransactionInferences.v10.key
    v11 = TransactionInferences.v11.key
    v12 = TransactionInferences.v12.key
    v13 = TransactionInferences.v13.key
    v14 = TransactionInferences.v14.key
    v15 = TransactionInferences.v15.key
    v16 = TransactionInferences.v16.key
    v17 = TransactionInferences.v17.key
    v18 = TransactionInferences.v18.key
    v19 = TransactionInferences.v19.key
    v20 = TransactionInferences.v20.key
    v21 = TransactionInferences.v21.key
    v22 = TransactionInferences.v22.key
    v23 = TransactionInferences.v23.key
    v24 = TransactionInferences.v24.key
    v25 = TransactionInferences.v25.key
    v26 = TransactionInferences.v26.key
    v27 = TransactionInferences.v27.key
    v28 = TransactionInferences.v28.key