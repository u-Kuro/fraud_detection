import boto3
from botocore.config import Config, _S3Dict

s3_client = boto3.client(
    "s3",
    config=Config(s3=_S3Dict(addressing_style="path"))
)
