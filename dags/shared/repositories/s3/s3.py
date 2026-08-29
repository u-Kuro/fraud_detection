from airflow.providers.amazon.aws.hooks.s3 import S3Hook

from dags.shared.modules.environment.s3 import s3_environment

s3_hook = S3Hook(aws_conn_id=s3_environment.S3_CONNECTION_ID)