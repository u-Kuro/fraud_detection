from airflow.providers.amazon.aws.hooks.s3 import S3Hook

from dags.shared.modules.configs import s3_config

s3_hook = S3Hook(aws_conn_id=s3_config.S3_CONNECTION_ID)