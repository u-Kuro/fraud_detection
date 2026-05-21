CREATE TABLE IF NOT EXISTS deployed_models (
    model_id                SERIAL              NOT NULL        PRIMARY KEY,
    model_name              TEXT                NOT NULL,
    model_version           INT                 NOT NULL,
    UNIQUE (model_name, model_version)
);

CREATE TABLE IF NOT EXISTS model_training_metadata (
    metadata_id             SERIAL              NOT NULL        PRIMARY KEY,
    training_timestamp      TIMESTAMPTZ         NOT NULL        DEFAULT NOW(),
    data_start_timestamp    TIMESTAMPTZ         NULL,
    data_end_timestamp      TIMESTAMPTZ         NOT NULL
);

CREATE TABLE IF NOT EXISTS transaction_inferences (
    request_id              UUID                NOT NULL        PRIMARY KEY     DEFAULT gen_random_uuid(),
    inference_timestamp     TIMESTAMPTZ         NOT NULL        DEFAULT NOW(),
    transaction_id          UUID                NULL,
    transaction_timestamp   TIMESTAMPTZ         NOT NULL,
    amount                  DOUBLE PRECISION    NOT NULL,
    is_fraud                BOOLEAN             NULL,
    is_fraud_prediction     BOOLEAN             NULL,
    is_fraud_probability    DOUBLE PRECISION    NULL            CHECK (is_fraud_probability BETWEEN 0 AND 1),
    model_deployment_id     INT                 NULL            REFERENCES      deployed_models(model_id),
    latency_ms              DOUBLE PRECISION    NULL,
    v1                      DOUBLE PRECISION    NOT NULL,
    v2                      DOUBLE PRECISION    NOT NULL,
    v3                      DOUBLE PRECISION    NOT NULL,
    v4                      DOUBLE PRECISION    NOT NULL,
    v5                      DOUBLE PRECISION    NOT NULL,
    v6                      DOUBLE PRECISION    NOT NULL,
    v7                      DOUBLE PRECISION    NOT NULL,
    v8                      DOUBLE PRECISION    NOT NULL,
    v9                      DOUBLE PRECISION    NOT NULL,
    v10                     DOUBLE PRECISION    NOT NULL,
    v11                     DOUBLE PRECISION    NOT NULL,
    v12                     DOUBLE PRECISION    NOT NULL,
    v13                     DOUBLE PRECISION    NOT NULL,
    v14                     DOUBLE PRECISION    NOT NULL,
    v15                     DOUBLE PRECISION    NOT NULL,
    v16                     DOUBLE PRECISION    NOT NULL,
    v17                     DOUBLE PRECISION    NOT NULL,
    v18                     DOUBLE PRECISION    NOT NULL,
    v19                     DOUBLE PRECISION    NOT NULL,
    v20                     DOUBLE PRECISION    NOT NULL,
    v21                     DOUBLE PRECISION    NOT NULL,
    v22                     DOUBLE PRECISION    NOT NULL,
    v23                     DOUBLE PRECISION    NOT NULL,
    v24                     DOUBLE PRECISION    NOT NULL,
    v25                     DOUBLE PRECISION    NOT NULL,
    v26                     DOUBLE PRECISION    NOT NULL,
    v27                     DOUBLE PRECISION    NOT NULL,
    v28                     DOUBLE PRECISION    NOT NULL
);