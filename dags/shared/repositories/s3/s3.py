from airflow.providers.amazon.aws.hooks.s3 import S3Hook

from dags.shared.modules.configs.s3 import S3Config

s3_hook = S3Hook(aws_conn_id=S3Config.S3_CONNECTION_ID)