DO $$
BEGIN
    -- transaction_inferences
    IF NOT EXISTS (SELECT 1 FROM transaction_inferences) THEN
        CREATE TEMP TABLE raw_data (
            "Time"      DOUBLE PRECISION,
            v1          DOUBLE PRECISION,
            v2          DOUBLE PRECISION,
            v3          DOUBLE PRECISION,
            v4          DOUBLE PRECISION,
            v5          DOUBLE PRECISION,
            v6          DOUBLE PRECISION,
            v7          DOUBLE PRECISION,
            v8          DOUBLE PRECISION,
            v9          DOUBLE PRECISION,
            v10         DOUBLE PRECISION,
            v11         DOUBLE PRECISION,
            v12         DOUBLE PRECISION,
            v13         DOUBLE PRECISION,
            v14         DOUBLE PRECISION,
            v15         DOUBLE PRECISION,
            v16         DOUBLE PRECISION,
            v17         DOUBLE PRECISION,
            v18         DOUBLE PRECISION,
            v19         DOUBLE PRECISION,
            v20         DOUBLE PRECISION,
            v21         DOUBLE PRECISION,
            v22         DOUBLE PRECISION,
            v23         DOUBLE PRECISION,
            v24         DOUBLE PRECISION,
            v25         DOUBLE PRECISION,
            v26         DOUBLE PRECISION,
            v27         DOUBLE PRECISION,
            v28         DOUBLE PRECISION,
            "Amount"    DOUBLE PRECISION,
            "Class"     BOOLEAN
        );

        COPY raw_data (
            "Time", v1, v2, v3, v4, v5, v6, v7, v8, v9, v10,
            v11, v12, v13, v14, v15, v16, v17, v18, v19, v20,
            v21, v22, v23, v24, v25, v26, v27, v28,
            "Amount",
            "Class"
        ) FROM PROGRAM 'gunzip -c /postgres/fraud_detection/raw_data/creditcard_transactions.csv.gz' WITH (FORMAT csv, HEADER true);
        INSERT INTO transaction_inferences (
            transaction_id,
            transaction_timestamp,
            v1,  v2,  v3,  v4,  v5,  v6,  v7,  v8,  v9,  v10,
            v11, v12, v13, v14, v15, v16, v17, v18, v19, v20,
            v21, v22, v23, v24, v25, v26, v27, v28,
            amount,
            is_fraud
        )
        SELECT
            gen_random_uuid(),
            -- '2019-01-01 00:00:00 UTC' used as the arbitrary base for the first transaction
            '2019-01-01 00:00:00+00'::timestamptz + ("Time" * interval '1 second'),
            v1,  v2,  v3,  v4,  v5,  v6,  v7,  v8,  v9,  v10,
            v11, v12, v13, v14, v15, v16, v17, v18, v19, v20,
            v21, v22, v23, v24, v25, v26, v27, v28,
            "Amount",
            "Class"
        FROM raw_data;
    END IF;

    -- model_training_metadata
    IF NOT EXISTS (SELECT 1 FROM model_training_metadata) AND EXISTS (SELECT 1 FROM transaction_inferences) THEN
        INSERT INTO model_training_metadata (
            data_start_timestamp,
            data_end_timestamp
        )
        SELECT
            MIN(transaction_timestamp),
            MAX(transaction_timestamp)
        FROM transaction_inferences;
    END IF;
END $$;