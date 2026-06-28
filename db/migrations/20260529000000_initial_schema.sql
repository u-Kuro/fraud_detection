CREATE TABLE projects (
    id                      UUID                NOT NULL        DEFAULT gen_random_uuid()       PRIMARY KEY,
    created_at              TIMESTAMPTZ         NOT NULL        DEFAULT NOW(),
    name                    TEXT                NOT NULL
);

CREATE TABLE model_deployments (
    id                      UUID                NOT NULL        DEFAULT gen_random_uuid()       PRIMARY KEY,
    created_at              TIMESTAMPTZ         NOT NULL        DEFAULT NOW(),
    project_id              UUID                NOT NULL                                        REFERENCES model_tasks(id),
    name                    TEXT                NOT NULL,
    version                 INT                 NOT NULL,
    dataset_min_date        TIMESTAMPTZ         NULL,
    dataset_max_date        TIMESTAMPTZ         NOT NULL,
    active                  BOOLEAN             NOT NULL        DEFAULT FALSE,
    CONSTRAINT model_deployment_name_version_key UNIQUE (name, version)
);

CREATE TABLE model_deployment_workflows (
    id                      UUID                NOT NULL        DEFAULT gen_random_uuid()       PRIMARY KEY,
    created_at              TIMESTAMPTZ         NOT NULL        DEFAULT NOW(),
    project_id              UUID                NOT NULL                                        REFERENCES model_tasks(id),
    state                   TEXT                NOT NULL,
    training_approved       BOOLEAN             NOT NULL        DEFAULT FALSE,
    promote_approved        BOOLEAN             NOT NULL        DEFAULT FALSE,
    run_id                  TEXT                NULL,
    model_version           INT                 NULL,
    dataset_min_date        TIMESTAMPTZ         NULL,
    dataset_max_date        TIMESTAMPTZ         NULL,
    drift_slack_ts          TEXT                NULL,
    promote_slack_ts        TEXT                NULL,
    CONSTRAINT state_check CHECK (state IN ('drift_pending', 'train_pending', 'promoting'))
);

CREATE TABLE transaction_inferences (
    id                      UUID                NOT NULL        DEFAULT gen_random_uuid()       PRIMARY KEY,
    created_at              TIMESTAMPTZ         NOT NULL        DEFAULT NOW(),
    transaction_id          UUID                NULL,
    transaction_timestamp   TIMESTAMPTZ         NOT NULL,
    amount                  DOUBLE PRECISION    NOT NULL,
    is_fraud                BOOLEAN             NULL,
    is_fraud_prediction     BOOLEAN             NULL,
    is_fraud_probability    DOUBLE PRECISION    NULL,
    deployed_model_id       INT                 NULL                                            REFERENCES model_deployments(id),
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