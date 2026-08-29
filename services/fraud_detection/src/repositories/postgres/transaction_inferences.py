from sqlalchemy import select, insert

from services.fraud_detection.src.modules.schemas.inferences.fraud_classification import FraudClassificationOutput
from services.fraud_detection.src.repositories.postgres.postgres import sql_session
from services.shared.modules.configs.postgres import PostgresConfig
from services.shared.modules.schemas.postgres.model_deployments import ModelDeployments
from services.shared.modules.schemas.postgres.transaction_inferences import TransactionInferences

def insert_transaction_inference(
    transaction_inference: FraudClassificationOutput,
    is_fraud: bool | None = None,
):
    with sql_session.begin() as session:
        model_deployment_id_subquery = (
            select(ModelDeployments.id)
            .where(
                ModelDeployments.project_id == PostgresConfig.project_id(),
                ModelDeployments.name == transaction_inference.model_name,
                ModelDeployments.version == transaction_inference.model_version,
            )
            .limit(1)
            .scalar_subquery()
        )

        session.execute(
            insert(TransactionInferences).values({
                TransactionInferences.transaction_id.key: transaction_inference.transaction_id,
                TransactionInferences.transaction_timestamp.key: transaction_inference.transaction_timestamp,
                TransactionInferences.amount.key: transaction_inference.amount,
                TransactionInferences.is_fraud.key: next((v for v in [is_fraud, transaction_inference.is_fraud] if isinstance(v, bool)), None),
                TransactionInferences.is_fraud_prediction.key: transaction_inference.is_fraud_prediction,
                TransactionInferences.is_fraud_probability.key: transaction_inference.is_fraud_probability,
                TransactionInferences.model_deployment_id.key: model_deployment_id_subquery,
                TransactionInferences.v1.key: transaction_inference.v1,
                TransactionInferences.v2.key: transaction_inference.v2,
                TransactionInferences.v3.key: transaction_inference.v3,
                TransactionInferences.v4.key: transaction_inference.v4,
                TransactionInferences.v5.key: transaction_inference.v5,
                TransactionInferences.v6.key: transaction_inference.v6,
                TransactionInferences.v7.key: transaction_inference.v7,
                TransactionInferences.v8.key: transaction_inference.v8,
                TransactionInferences.v9.key: transaction_inference.v9,
                TransactionInferences.v10.key: transaction_inference.v10,
                TransactionInferences.v11.key: transaction_inference.v11,
                TransactionInferences.v12.key: transaction_inference.v12,
                TransactionInferences.v13.key: transaction_inference.v13,
                TransactionInferences.v14.key: transaction_inference.v14,
                TransactionInferences.v15.key: transaction_inference.v15,
                TransactionInferences.v16.key: transaction_inference.v16,
                TransactionInferences.v17.key: transaction_inference.v17,
                TransactionInferences.v18.key: transaction_inference.v18,
                TransactionInferences.v19.key: transaction_inference.v19,
                TransactionInferences.v20.key: transaction_inference.v20,
                TransactionInferences.v21.key: transaction_inference.v21,
                TransactionInferences.v22.key: transaction_inference.v22,
                TransactionInferences.v23.key: transaction_inference.v23,
                TransactionInferences.v24.key: transaction_inference.v24,
                TransactionInferences.v25.key: transaction_inference.v25,
                TransactionInferences.v26.key: transaction_inference.v26,
                TransactionInferences.v27.key: transaction_inference.v27,
                TransactionInferences.v28.key: transaction_inference.v28,
            })
        )