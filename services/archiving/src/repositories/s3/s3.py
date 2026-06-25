# import boto3
# from services.archiving.src.modules.environment import environment
#
# s3_client = boto3.client(
#     "s3",
#     endpoint_url=environment.S3_ENDPOINT_URL,
#     aws_access_key_id=environment.S3_ACCESS_KEY,
#     aws_secret_access_key=environment.S3_SECRET_KEY,
# )