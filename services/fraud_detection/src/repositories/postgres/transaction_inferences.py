from sqlalchemy import select, insert

from services.fraud_detection.src.modules.schemas.inferences.fraud_classification import FraudClassificationOutput
from services.fraud_detection.src.repositories.postgres.postgres import sql_session
from services.shared.modules.configs.postgres import PostgresConfig
from services.shared.modules.schemas.postgres.model_deployments import ModelDeployment
from services.shared.modules.schemas.postgres.transaction_inferences import TransactionInference

def insert_transaction_inference(
    transaction_inference: FraudClassificationOutput,
    is_fraud: bool | None = None,
):
    with sql_session.begin() as session:
        model_deployment_id_subquery = (
            select(ModelDeployment.id)
            .where(
                ModelDeployment.project_id == PostgresConfig.PROJECT_ID(),
                ModelDeployment.name == transaction_inference.model_name,
                ModelDeployment.version == transaction_inference.model_version,
            )
            .limit(1)
            .scalar_subquery()
        )

        session.execute(
            insert(TransactionInference).values({
                TransactionInference.transaction_id.key: transaction_inference.transaction_id,
                TransactionInference.transaction_timestamp.key: transaction_inference.transaction_timestamp,
                TransactionInference.amount.key: transaction_inference.amount,
                TransactionInference.is_fraud.key: next((v for v in [is_fraud, transaction_inference.is_fraud] if isinstance(v, bool)), None),
                TransactionInference.is_fraud_prediction.key: transaction_inference.is_fraud_prediction,
                TransactionInference.is_fraud_probability.key: transaction_inference.is_fraud_probability,
                TransactionInference.model_deployment_id.key: model_deployment_id_subquery,
                TransactionInference.v1.key: transaction_inference.v1,
                TransactionInference.v2.key: transaction_inference.v2,
                TransactionInference.v3.key: transaction_inference.v3,
                TransactionInference.v4.key: transaction_inference.v4,
                TransactionInference.v5.key: transaction_inference.v5,
                TransactionInference.v6.key: transaction_inference.v6,
                TransactionInference.v7.key: transaction_inference.v7,
                TransactionInference.v8.key: transaction_inference.v8,
                TransactionInference.v9.key: transaction_inference.v9,
                TransactionInference.v10.key: transaction_inference.v10,
                TransactionInference.v11.key: transaction_inference.v11,
                TransactionInference.v12.key: transaction_inference.v12,
                TransactionInference.v13.key: transaction_inference.v13,
                TransactionInference.v14.key: transaction_inference.v14,
                TransactionInference.v15.key: transaction_inference.v15,
                TransactionInference.v16.key: transaction_inference.v16,
                TransactionInference.v17.key: transaction_inference.v17,
                TransactionInference.v18.key: transaction_inference.v18,
                TransactionInference.v19.key: transaction_inference.v19,
                TransactionInference.v20.key: transaction_inference.v20,
                TransactionInference.v21.key: transaction_inference.v21,
                TransactionInference.v22.key: transaction_inference.v22,
                TransactionInference.v23.key: transaction_inference.v23,
                TransactionInference.v24.key: transaction_inference.v24,
                TransactionInference.v25.key: transaction_inference.v25,
                TransactionInference.v26.key: transaction_inference.v26,
                TransactionInference.v27.key: transaction_inference.v27,
                TransactionInference.v28.key: transaction_inference.v28,
            })
        )