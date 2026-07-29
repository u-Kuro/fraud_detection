from sqlalchemy import text

from services.fraud_detection.src.modules.schemas.inferences.fraud_classification import FraudClassificationOutput
from services.fraud_detection.src.repositories.postgres.postgres import engine
from services.shared.modules.configs.postgres import PostgresConfig
from services.shared.modules.schemas.postgres.model_deployments import ModelDeploymentsColumnKeys
from services.shared.modules.schemas.postgres.postgres import PostgresTableKeys
from services.shared.modules.schemas.postgres.transaction_inferences import TransactionInferencesColumnKeys

def insert_transaction_inference(
    transaction_inference: FraudClassificationOutput,
    is_fraud: bool | None = None,
):
    with engine.connect() as connection:
        connection.execute(
            text(f"""
                WITH active_model AS (
                    SELECT {ModelDeploymentsColumnKeys.id}
                    FROM {PostgresTableKeys.model_deployments}
                    WHERE 
                        {ModelDeploymentsColumnKeys.project_id} = :{ModelDeploymentsColumnKeys.project_id}
                    AND {ModelDeploymentsColumnKeys.name} = :{ModelDeploymentsColumnKeys.name}
                    AND {ModelDeploymentsColumnKeys.version} = :{ModelDeploymentsColumnKeys.version}
                    LIMIT 1
                )
                INSERT INTO {PostgresTableKeys.transaction_inferences}(
                    {TransactionInferencesColumnKeys.transaction_id},
                    {TransactionInferencesColumnKeys.transaction_timestamp},
                    {TransactionInferencesColumnKeys.amount},
                    {TransactionInferencesColumnKeys.is_fraud},
                    {TransactionInferencesColumnKeys.is_fraud_prediction},
                    {TransactionInferencesColumnKeys.is_fraud_probability},
                    {TransactionInferencesColumnKeys.deployed_model_id},
                    {TransactionInferencesColumnKeys.v1},
                    {TransactionInferencesColumnKeys.v2},
                    {TransactionInferencesColumnKeys.v3},
                    {TransactionInferencesColumnKeys.v4},
                    {TransactionInferencesColumnKeys.v5},
                    {TransactionInferencesColumnKeys.v6},
                    {TransactionInferencesColumnKeys.v7},
                    {TransactionInferencesColumnKeys.v8},
                    {TransactionInferencesColumnKeys.v9},
                    {TransactionInferencesColumnKeys.v10},
                    {TransactionInferencesColumnKeys.v11},
                    {TransactionInferencesColumnKeys.v12},
                    {TransactionInferencesColumnKeys.v13},
                    {TransactionInferencesColumnKeys.v14},
                    {TransactionInferencesColumnKeys.v15},
                    {TransactionInferencesColumnKeys.v16},
                    {TransactionInferencesColumnKeys.v17},
                    {TransactionInferencesColumnKeys.v18},
                    {TransactionInferencesColumnKeys.v19},
                    {TransactionInferencesColumnKeys.v20},
                    {TransactionInferencesColumnKeys.v21},
                    {TransactionInferencesColumnKeys.v22},
                    {TransactionInferencesColumnKeys.v23},
                    {TransactionInferencesColumnKeys.v24},
                    {TransactionInferencesColumnKeys.v25},
                    {TransactionInferencesColumnKeys.v26},
                    {TransactionInferencesColumnKeys.v27},
                    {TransactionInferencesColumnKeys.v28}
                )
                VALUES(
                    :{TransactionInferencesColumnKeys.transaction_id},
                    :{TransactionInferencesColumnKeys.transaction_timestamp},
                    :{TransactionInferencesColumnKeys.amount},
                    :{TransactionInferencesColumnKeys.is_fraud},
                    :{TransactionInferencesColumnKeys.is_fraud_prediction},
                    :{TransactionInferencesColumnKeys.is_fraud_probability},
                    (SELECT {ModelDeploymentsColumnKeys.id} FROM active_model),
                    :{TransactionInferencesColumnKeys.v1},
                    :{TransactionInferencesColumnKeys.v2},
                    :{TransactionInferencesColumnKeys.v3},
                    :{TransactionInferencesColumnKeys.v4},
                    :{TransactionInferencesColumnKeys.v5},
                    :{TransactionInferencesColumnKeys.v6},
                    :{TransactionInferencesColumnKeys.v7},
                    :{TransactionInferencesColumnKeys.v8},
                    :{TransactionInferencesColumnKeys.v9},
                    :{TransactionInferencesColumnKeys.v10},
                    :{TransactionInferencesColumnKeys.v11},
                    :{TransactionInferencesColumnKeys.v12},
                    :{TransactionInferencesColumnKeys.v13},
                    :{TransactionInferencesColumnKeys.v14},
                    :{TransactionInferencesColumnKeys.v15},
                    :{TransactionInferencesColumnKeys.v16},
                    :{TransactionInferencesColumnKeys.v17},
                    :{TransactionInferencesColumnKeys.v18},
                    :{TransactionInferencesColumnKeys.v19},
                    :{TransactionInferencesColumnKeys.v20},
                    :{TransactionInferencesColumnKeys.v21},
                    :{TransactionInferencesColumnKeys.v22},
                    :{TransactionInferencesColumnKeys.v23},
                    :{TransactionInferencesColumnKeys.v24},
                    :{TransactionInferencesColumnKeys.v25},
                    :{TransactionInferencesColumnKeys.v26},
                    :{TransactionInferencesColumnKeys.v27},
                    :{TransactionInferencesColumnKeys.v28}
                )
            """),
            {
                ModelDeploymentsColumnKeys.project_id: PostgresConfig.PROJECT_ID(),
                ModelDeploymentsColumnKeys.name: transaction_inference.model_name,
                ModelDeploymentsColumnKeys.version: transaction_inference.model_version,
                TransactionInferencesColumnKeys.transaction_id: transaction_inference.transaction_id,
                TransactionInferencesColumnKeys.transaction_timestamp: transaction_inference.transaction_timestamp,
                TransactionInferencesColumnKeys.amount: transaction_inference.amount,
                TransactionInferencesColumnKeys.is_fraud: (
                    is_fraud
                    if is_fraud is not None
                    else transaction_inference.is_fraud
                ),
                TransactionInferencesColumnKeys.is_fraud_prediction: transaction_inference.is_fraud_prediction,
                TransactionInferencesColumnKeys.is_fraud_probability: transaction_inference.is_fraud_probability,
                TransactionInferencesColumnKeys.v1: transaction_inference.v1,
                TransactionInferencesColumnKeys.v2: transaction_inference.v2,
                TransactionInferencesColumnKeys.v3: transaction_inference.v3,
                TransactionInferencesColumnKeys.v4: transaction_inference.v4,
                TransactionInferencesColumnKeys.v5: transaction_inference.v5,
                TransactionInferencesColumnKeys.v6: transaction_inference.v6,
                TransactionInferencesColumnKeys.v7: transaction_inference.v7,
                TransactionInferencesColumnKeys.v8: transaction_inference.v8,
                TransactionInferencesColumnKeys.v9: transaction_inference.v9,
                TransactionInferencesColumnKeys.v10: transaction_inference.v10,
                TransactionInferencesColumnKeys.v11: transaction_inference.v11,
                TransactionInferencesColumnKeys.v12: transaction_inference.v12,
                TransactionInferencesColumnKeys.v13: transaction_inference.v13,
                TransactionInferencesColumnKeys.v14: transaction_inference.v14,
                TransactionInferencesColumnKeys.v15: transaction_inference.v15,
                TransactionInferencesColumnKeys.v16: transaction_inference.v16,
                TransactionInferencesColumnKeys.v17: transaction_inference.v17,
                TransactionInferencesColumnKeys.v18: transaction_inference.v18,
                TransactionInferencesColumnKeys.v19: transaction_inference.v19,
                TransactionInferencesColumnKeys.v20: transaction_inference.v20,
                TransactionInferencesColumnKeys.v21: transaction_inference.v21,
                TransactionInferencesColumnKeys.v22: transaction_inference.v22,
                TransactionInferencesColumnKeys.v23: transaction_inference.v23,
                TransactionInferencesColumnKeys.v24: transaction_inference.v24,
                TransactionInferencesColumnKeys.v25: transaction_inference.v25,
                TransactionInferencesColumnKeys.v26: transaction_inference.v26,
                TransactionInferencesColumnKeys.v27: transaction_inference.v27,
                TransactionInferencesColumnKeys.v28: transaction_inference.v28
            },
        )
        connection.commit()