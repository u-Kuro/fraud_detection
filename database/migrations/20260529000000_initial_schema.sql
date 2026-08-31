CREATE TABLE projects (
    id                      UUID                NOT NULL        DEFAULT gen_random_uuid()       PRIMARY KEY,
    created_at              TIMESTAMPTZ         NOT NULL        DEFAULT NOW(),
    name                    TEXT                NOT NULL,
    CONSTRAINT unique_project_name UNIQUE (name)
);

CREATE TABLE model_deployment_workflows (
    id                                      UUID                NOT NULL        DEFAULT gen_random_uuid()       PRIMARY KEY,
    created_at                              TIMESTAMPTZ         NOT NULL        DEFAULT NOW(),
    project_id                              UUID                NOT NULL                                        REFERENCES projects(id),
    state                                   TEXT                NOT NULL,
    training_approved                       BOOLEAN             NOT NULL        DEFAULT FALSE,
    promotion_approved                      BOOLEAN             NOT NULL        DEFAULT FALSE,
    model_trained_at                        TIMESTAMPTZ         NOT NULL,
    mlflow_run_id                           TEXT                NULL,
    registered_model_name                   TEXT                NULL,
    registered_model_version                INT                 NULL,
    model_dataset_min_timestamp             TIMESTAMPTZ         NULL,
    model_dataset_max_timestamp             TIMESTAMPTZ         NULL,
    slack_training_approval_message_ts      TEXT                NOT NULL,
    slack_promotion_approval_message_ts     TEXT                NULL,
    CONSTRAINT state_check CHECK (state IN ('train_pending', 'promote_pending', 'reserved')),
);

CREATE TABLE model_deployments (
    id                      UUID                NOT NULL        DEFAULT gen_random_uuid()       PRIMARY KEY,
    created_at              TIMESTAMPTZ         NOT NULL        DEFAULT NOW(),
    project_id              UUID                NOT NULL                                        REFERENCES projects(id),
    name                    TEXT                NOT NULL,
    version                 INT                 NOT NULL,
    mlflow_run_id           TEXT                NOT NULL,
    dataset_min_timestamp   TIMESTAMPTZ         NOT NULL,
    dataset_max_timestamp   TIMESTAMPTZ         NOT NULL,
    active                  BOOLEAN             NOT NULL        DEFAULT FALSE,
    CONSTRAINT model_deployment_name_version_key UNIQUE (name, version)
);
CREATE UNIQUE INDEX one_active_model_deployment_per_project ON model_deployments (project_id) WHERE active = TRUE;

CREATE TABLE transaction_inferences (
    id                      UUID                NOT NULL        DEFAULT gen_random_uuid()       PRIMARY KEY,
    created_at              TIMESTAMPTZ         NOT NULL        DEFAULT NOW(),
    transaction_id          UUID                NULL,
    transaction_timestamp   TIMESTAMPTZ         NOT NULL,
    amount                  DOUBLE PRECISION    NOT NULL,
    is_fraud                BOOLEAN             NULL,
    is_fraud_prediction     BOOLEAN             NULL,
    is_fraud_probability    DOUBLE PRECISION    NULL,
    model_deployment_id     UUID                NULL                                            REFERENCES model_deployments(id),
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
    v28                     DOUBLE PRECISION    NOT NULL,
    CONSTRAINT transaction_inferences_is_fraud_probability_check CHECK (is_fraud_probability BETWEEN 0 AND 1)
);