import boto3
from botocore.config import Config

s3_client = boto3.client(
    service_name="s3",
    config=Config(s3={"addressing_style": "path"})
)
