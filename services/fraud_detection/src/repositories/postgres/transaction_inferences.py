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
            insert(TransactionInference).values(
                transaction_id=transaction_inference.transaction_id,
                transaction_timestamp=transaction_inference.transaction_timestamp,
                amount=transaction_inference.amount,
                is_fraud=(
                    is_fraud
                    if is_fraud is not None
                    else transaction_inference.is_fraud
                ),
                is_fraud_prediction=transaction_inference.is_fraud_prediction,
                is_fraud_probability=transaction_inference.is_fraud_probability,
                model_deployment_id=model_deployment_id_subquery,
                v1=transaction_inference.v1,
                v2=transaction_inference.v2,
                v3=transaction_inference.v3,
                v4=transaction_inference.v4,
                v5=transaction_inference.v5,
                v6=transaction_inference.v6,
                v7=transaction_inference.v7,
                v8=transaction_inference.v8,
                v9=transaction_inference.v9,
                v10=transaction_inference.v10,
                v11=transaction_inference.v11,
                v12=transaction_inference.v12,
                v13=transaction_inference.v13,
                v14=transaction_inference.v14,
                v15=transaction_inference.v15,
                v16=transaction_inference.v16,
                v17=transaction_inference.v17,
                v18=transaction_inference.v18,
                v19=transaction_inference.v19,
                v20=transaction_inference.v20,
                v21=transaction_inference.v21,
                v22=transaction_inference.v22,
                v23=transaction_inference.v23,
                v24=transaction_inference.v24,
                v25=transaction_inference.v25,
                v26=transaction_inference.v26,
                v27=transaction_inference.v27,
                v28=transaction_inference.v28,
            )
        )