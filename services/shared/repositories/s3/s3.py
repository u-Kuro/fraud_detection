import boto3
from botocore.config import Config, _S3Dict

from mypy_boto3_s3.client import S3Client

s3_client: S3Client = boto3.client(
    "s3",
    config=Config(s3=_S3Dict(addressing_style="path"))
)
