import boto3
from botocore.config import Config, _S3Dict

from mypy_boto3_s3.client import S3Client

"""
    Create a boto3 S3 client from standard AWS environment variables only.

    Reads automatically from env (supplied by platform-infra ConfigMap + MLE secret):
      AWS_ACCESS_KEY_ID      — from MLE k8s secret
      AWS_SECRET_ACCESS_KEY  — from MLE k8s secret
      AWS_DEFAULT_REGION     — from platform-infra ConfigMap
      AWS_ENDPOINT_URL_S3    — from platform-infra ConfigMap (ministack endpoint)

    Forces path-style addressing for ministack/localstack compatibility.
"""
s3_client: S3Client = boto3.client(
    "s3",
    config=Config(s3=_S3Dict(addressing_style="path"))
)
